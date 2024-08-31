import os
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.timezone import now
from Tennis_training_system import settings
from . import forms
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.shortcuts import get_object_or_404
from .forms import EmailAuthenticationForm,  GameForm, CourtForm, CategoryForm, ProfilePictureUpdateForm, CustomPasswordChangeForm
from django.views.generic import FormView, TemplateView, View
from .models import Game, Category, Participant
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta, datetime
from django.http import JsonResponse, Http404
import logging

logger = logging.getLogger(__name__)


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class CustomLoginView(FormView):
    form_class = EmailAuthenticationForm
    template_name = 'login.html'
    success_url = reverse_lazy('day')
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=email, password=password)

        if user is not None:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, 'Invalid email or password.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)


class DayView(LoginRequiredMixin, TemplateView):
    model = Game
    template_name = 'day.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_base_context())
        if self.request.user.is_staff:
            context.update(self.get_staff_context())
        return context

    def get_base_context(self):
        return {
            'hours': range(1, 24),
            'breaklines': range(23),
            'game_form': GameForm(),
            'categories': Category.objects.all(),
        }

    def get_staff_context(self):
        return {
            'court_form': CourtForm(),
            'category_form': CategoryForm(),
        }

    def get(self, request, *args, **kwargs):
        if self.is_ajax(request):
            if 'fetch_game_details' in request.GET and 'game_id' in request.GET:
                game_id = request.GET.get('game_id')
                game = get_object_or_404(Game, game_id=game_id)
                game_data = {
                    'name': game.name,
                    'start_date_and_time': game.start_date_and_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_date_and_time': game.end_date_and_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'category': game.category.category_id,
                    'category_name': game.category.name,
                    'court': game.court.court_id,
                    'court_name': game.court.name,
                    'participants': list(game.participant_set.values_list('user__email', 'user__username')),
                    'is_creator': (game.creator == request.user),
                }
                return JsonResponse(game_data)

            date_str = request.GET.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now().date()
            events, date_info = self.get_events_and_date_info(date)
            return JsonResponse({
                'events': events,
                **date_info,
            })
        else:
            return super().get(request, *args, **kwargs)

    def is_ajax(self, request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'XMLHttpRequest' in request.headers.get(
            'X-Requested-With', '')

    def get_events_and_date_info(self, date):
        user = self.request.user

        events_query = Game.objects.filter(
            start_date_and_time__date=date,
            participant__user=user
        ).values(
            'game_id',
            'name',
            'category__name',
            'category__color',
            'start_date_and_time',
            'end_date_and_time',
            'creator',
            'creator__profile_picture'
        )

        events = list(events_query)

        for event in events:
            event['start_date_and_time'] = event['start_date_and_time'].strftime('%Y-%m-%d %H:%M:%S')
            event['end_date_and_time'] = event['end_date_and_time'].strftime('%Y-%m-%d %H:%M:%S')
            start_time = event['start_date_and_time'].split(' ')[1]
            end_time = event['end_date_and_time'].split(' ')[1]
            start_time_minutes = self.convert_string_time_to_minutes(start_time)
            end_time_minutes = self.convert_string_time_to_minutes(end_time)
            duration = end_time_minutes - start_time_minutes
            event['margin_top'] = (start_time_minutes / 60) * 100
            event['height'] = (duration / 60) * 100

            profile_picture = event.get('creator__profile_picture', '')
            if profile_picture:
                event['profile_picture_url'] = f"{settings.MEDIA_URL}{profile_picture}"
            else:
                event['profile_picture_url'] = settings.STATIC_URL + 'images/Ola.png'

            event['is_creator'] = (event['creator'] == self.request.user.user_id)

        date_info = {
            'current_date': date.strftime('%d %B %Y'),
            'prev_date': (date - timedelta(days=1)).strftime('%Y-%m-%d'),
            'next_date': (date + timedelta(days=1)).strftime('%Y-%m-%d'),
        }

        return events, date_info

    def convert_string_time_to_minutes(self, time_str):
        hours, minutes, _ = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def post(self, request, *args, **kwargs):
        if self.is_ajax(request):
            if 'update_game' in request.POST and request.POST.get('game_id'):
                return self.handle_game_update(request)

            elif 'submit_game' in request.POST:
                return self.handle_game_form(request)

            elif 'delete_game' in request.POST:
                return self.handle_game_delete(request)

            elif 'submit_court' in request.POST:
                return self.handle_court_form(request)

            elif 'submit_category' in request.POST:
                return self.handle_category_form(request)

        return JsonResponse({'error': 'Invalid request'}, status=400)

    def handle_game_form(self, request):
        game_form = GameForm(request.POST)
        if game_form.is_valid():
            game = game_form.save(commit=False)
            game.creator = self.request.user
            game.save()

            participants = game_form.cleaned_data.get('participants', [])
            print("Validated participants:", participants)

            for user in participants:
                Participant.objects.create(user=user, game=game)

            game_form.save_m2m()

            recurrence_type = game_form.cleaned_data.get('recurrence_type')
            end_date_of_recurrence = game_form.cleaned_data.get('end_date_of_recurrence')

            if recurrence_type and end_date_of_recurrence:
                current_start = game.start_date_and_time
                current_end = game.end_date_and_time

                while current_start.date() <= end_date_of_recurrence:
                    if current_start != game.start_date_and_time:
                        new_game = Game.objects.create(
                            name=game.name,
                            category=game.category,
                            court=game.court,
                            creator=game.creator,
                            start_date_and_time=current_start,
                            end_date_and_time=current_end,
                            group=game.group
                        )

                        for user in participants:
                            Participant.objects.create(user=user, game=new_game)

                    if recurrence_type == 'daily':
                        current_start += timedelta(days=1)
                        current_end += timedelta(days=1)
                    elif recurrence_type == 'weekly':
                        current_start += timedelta(weeks=1)
                        current_end += timedelta(weeks=1)
                    elif recurrence_type == 'biweekly':
                        current_start += timedelta(weeks=2)
                        current_end += timedelta(weeks=2)
                    elif recurrence_type == 'monthly':
                        current_start = current_start.replace(month=current_start.month + 1)
                        current_end = current_end.replace(month=current_end.month + 1)

            return JsonResponse({'success': True, 'message': 'Game added successfully'})

        return JsonResponse({'success': False, 'errors': game_form.errors.as_json()}, status=400)

    def handle_game_update(self, request):
        print("Handling game update...")
        game_id = request.POST.get('game_id')

        if not game_id:
            print("No game ID provided in the request.")
            return JsonResponse({'success': False, 'message': 'Game ID is required.'}, status=400)

        try:
            game = get_object_or_404(Game, game_id=game_id, creator=request.user)
        except Http404:
            print(f"Game with ID {game_id} not found or user is not the creator.")
            return JsonResponse({'success': False, 'message': 'Game not found or permission denied.'}, status=404)

        form = GameForm(request.POST, instance=game)

        if form.is_valid():
            print(f"Form is valid. Saving game...{game_id}")
            updated_game = form.save(commit=False)  # Save the form to get the updated game instance
            updated_game.game_id = game_id
            game.save()
            # Handle participants only after form is valid
            participants = form.cleaned_data.get('participants', [])
            print("Validated participants:", participants)

            # Clear existing participants and add the updated ones
            updated_game.participant_set.all().delete()  # Remove current participants

            for user in participants:
                Participant.objects.create(user=user, game=updated_game)

            # Save many-to-many relationships, if any
            form.save_m2m()

            return JsonResponse({'success': True, 'message': 'Game updated successfully'})
        else:
            print("Form is invalid. Errors:", form.errors)
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)

    def handle_game_delete(self, request):
        game_id = request.POST.get('game_id')
        game = get_object_or_404(Game, game_id=game_id, creator=request.user)

        if game.creator == request.user:
            game.delete()
            return JsonResponse({'success': True, 'message': 'Game deleted successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'You do not have permission to delete this game'},
                                status=403)

    def handle_court_form(self, request):
        court_form = CourtForm(request.POST)
        if court_form.is_valid():
            court_form.save()
            return JsonResponse({'success': True, 'message': 'Court added successfully'})

        return JsonResponse({'success': False, 'errors': court_form.errors.as_json()}, status=400)

    def handle_category_form(self, request):
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return JsonResponse({'success': True, 'message': 'Category added successfully'})

        return JsonResponse({'success': False, 'errors': category_form.errors.as_json()}, status=400)

class UsersProfile(LoginRequiredMixin, View):
    template_name = 'users_profile.html'

    def get(self, request):
        profile_form = ProfilePictureUpdateForm()
        password_form = CustomPasswordChangeForm(user=request.user)

        context = {
            'profile_form': profile_form,
            'password_form': password_form,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, self.template_name, context)

    def save_profile_picture(self, profile_picture):
        file_name = profile_picture.name
        file_path = os.path.join('profile_pictures', file_name)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'wb+') as destination:
            for chunk in profile_picture.chunks():
                destination.write(chunk)

        return file_path

    def post(self, request):
        if 'profile_picture' in request.FILES:
            profile_form = ProfilePictureUpdateForm(request.POST, request.FILES)
            if profile_form.is_valid():
                profile_picture = profile_form.cleaned_data['profile_picture']
                file_path = self.save_profile_picture(profile_picture)
                request.user.profile_picture = file_path
                request.user.save()
                messages.success(request, 'Your profile picture has been updated.')
            else:
                messages.error(request, 'There has been an error while updating the profile picture.')

        elif 'old_password' in request.POST:
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated.')
            else:
                messages.error(request, 'Please correct the error below.')

        profile_form = ProfilePictureUpdateForm()
        password_form = CustomPasswordChangeForm(user=request.user)

        context = {
            'profile_form': profile_form,
            'password_form': password_form,
        }
        return render(request, self.template_name, context)


class WeekView(LoginRequiredMixin, TemplateView):
    template_name = 'week.html'