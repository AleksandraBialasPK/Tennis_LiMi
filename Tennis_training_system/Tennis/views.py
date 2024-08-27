import os
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.timezone import now
from Tennis_training_system import settings
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext_lazy as _
from .forms import EmailAuthenticationForm,  GameForm, CourtForm, CategoryForm, ProfilePictureUpdateForm, CustomPasswordChangeForm
from django.views.generic import FormView, ListView, TemplateView, CreateView, View
from .models import Game, Category
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import timedelta, datetime
from django.http import JsonResponse
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
        events_query = Game.objects.filter(start_date_and_time__date=date).values(
            'name', 'category__name', 'category__color', 'start_date_and_time', 'end_date_and_time', 'creator__profile_picture'
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
        print("Received POST request.")
        if self.is_ajax(request):
            print("AJAX request detected.")
            print("POST data:", request.POST)
            if 'submit_game' in request.POST:
                print("Handling game form.")
                return self.handle_game_form(request)

            if 'submit_court' in request.POST:
                print("Handling court form.")
                return self.handle_court_form(request)

            if 'submit_category' in request.POST:
                print("Handling category form.")
                return self.handle_category_form(request)

        print("Invalid request.")
        return JsonResponse({'error': 'Invalid request'}, status=400)

    def handle_game_form(self, request):
        game_form = GameForm(request.POST)
        if game_form.is_valid():
            game = game_form.save(commit=False)
            game.creator = self.request.user
            game.save()
            return JsonResponse({'success': True, 'message': 'Game added successfully'})
        return JsonResponse({'success': False, 'errors': game_form.errors.as_json()}, status=400)

    def handle_court_form(self, request):
        court_form = CourtForm(request.POST)
        if court_form.is_valid():
            court_form.save()
            print("Court added successfully")
            return JsonResponse({'success': True, 'message': 'Court added successfully'})
        # Correct use of .as_json() on court_form.errors
        print(court_form.errors)
        return JsonResponse({'success': False, 'errors': court_form.errors.as_json()}, status=400)

    def handle_category_form(self, request):
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            print("Category added successfully")
            return JsonResponse({'success': True, 'message': 'Category added successfully'})
        # Correct use of .as_json() on category_form.errors
        print(category_form.errors)
        return JsonResponse({'success': False, 'errors': category_form.errors.as_json()}, status=400)


class UsersProfile(LoginRequiredMixin, View):
    template_name = 'users_profile.html'

    def get(self, request):
        # Instantiate forms
        profile_form = ProfilePictureUpdateForm()
        password_form = CustomPasswordChangeForm(user=request.user)

        context = {
            'profile_form': profile_form,
            'password_form': password_form,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, self.template_name, context)

    def save_profile_picture(self, profile_picture):
        # Define the path where the file will be saved
        file_name = profile_picture.name
        file_path = os.path.join('profile_pictures', file_name)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Save the file to the specified path
        with open(full_path, 'wb+') as destination:
            for chunk in profile_picture.chunks():
                destination.write(chunk)

        return file_path

    def post(self, request):
        if 'profile_picture' in request.FILES:
            # Handling profile picture update
            print("this is the first if in the loop")
            profile_form = ProfilePictureUpdateForm(request.POST, request.FILES)
            if profile_form.is_valid():
                # Save the profile picture and update the path in the user profile
                print("profile form is valid")
                profile_picture = profile_form.cleaned_data['profile_picture']
                file_path = self.save_profile_picture(profile_picture)
                request.user.profile_picture = file_path
                request.user.save()
                messages.success(request, 'Your profile picture has been updated.')
            else:
                messages.error(request, 'There has been an error while updating the profile picture.')
                print("Profile form errors:", profile_form.errors)

        elif 'old_password' in request.POST:
            # Handling password change
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important! Keeps the user logged in
                messages.success(request, 'Your password has been updated.')
            else:
                messages.error(request, 'Please correct the error below.')

        # Re-render the forms
        profile_form = ProfilePictureUpdateForm()
        password_form = CustomPasswordChangeForm(user=request.user)

        context = {
            'profile_form': profile_form,
            'password_form': password_form,
        }
        return render(request, self.template_name, context)

class WeekView(LoginRequiredMixin, TemplateView):
    template_name = 'week.html'