from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.timezone import now, make_aware
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _
from .forms import EmailAuthenticationForm,  GameForm, CourtForm, CategoryForm
from django.views.generic import FormView, ListView, TemplateView, CreateView, View
from .models import Game, RecurringGroup, Participant, Category, Court
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import timedelta, datetime, date, time
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.template.loader import render_to_string
import logging
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = EmailAuthenticationForm
    success_url = reverse_lazy('day')

    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.info(self.request, _(f"You are now logged in as {email}."))
            return redirect(self.success_url)
        else:
            messages.error(self.request, _("Invalid email or password."))
            return self.form_invalid(form)


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
        }

    def get_staff_context(self):
        return {
            'court_form': CourtForm(),
            'category_form': CategoryForm(),
        }

    def get(self, request, *args, **kwargs):
        print("Request headers:", request.headers)
        if self.is_ajax(request):
            date_str = request.GET.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now().date()
            events, date_info = self.get_events_and_date_info(date)
            print("Events to be sent:", events)
            print("Date info to be sent:", date_info)
            return JsonResponse({
                'events': events,
                **date_info,
            })
        else:
            print("Non-AJAX request received, rendering full HTML.")
            return super().get(request, *args, **kwargs)

    def is_ajax(self, request):
        return request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'XMLHttpRequest' in request.headers.get(
            'X-Requested-With', '')

    def get_events_and_date_info(self, date):
        events_query = Game.objects.filter(start_date_and_time__date=date).values(
            'name', 'category__name', 'start_date_and_time', 'end_date_and_time'
        )

        events = list(events_query)
        print(f"Fetched events for {date}: {events}")

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

        date_info = {
            'current_date': date.strftime('%d %B %Y'),
            'prev_date': (date - timedelta(days=1)).strftime('%Y-%m-%d'),
            'next_date': (date + timedelta(days=1)).strftime('%Y-%m-%d'),
        }

        print(f"Returning date info: {date_info}")
        return events, date_info

    def convert_string_time_to_minutes(self, time_str):
        hours, minutes, _ = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if 'submit_game' in request.POST:
                return self.handle_game_form(request)

            if 'submit_court' in request.POST:
                return self.handle_court_form(request)

            if 'submit_category' in request.POST:
                return self.handle_category_form(request)

        return JsonResponse({'error': 'Invalid request'}, status=400)

    def handle_game_form(self, request):
        game_form = GameForm(request.POST)
        if game_form.is_valid():
            self.save_game(game_form)
            return JsonResponse({'success': True, 'message': 'Game added successfully'})
        return JsonResponse({'success': False, 'errors': game_form.errors})

    def handle_court_form(self, request):
        court_form = CourtForm(request.POST)
        if court_form.is_valid():
            court_form.save()
            return JsonResponse({'success': True, 'message': 'Court added successfully'})
        return JsonResponse({'success': False, 'errors': court_form.errors})

    def handle_category_form(self, request):
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return JsonResponse({'success': True, 'message': 'Category added successfully'})
        return JsonResponse({'success': False, 'errors': category_form.errors})

    def save_game(self, game_form):
        game = game_form.save(commit=False)
        game.creator = self.request.user
        game.save()
        return game

    # def post(self, request, *args, **kwargs):
    #     logger.info("Received POST request.")
    #     game_form = GameForm(request.POST)
    #     court_form = CourtForm(request.POST)
    #     category_form = CategoryForm(request.POST)
    #
    #     if 'submit_game' in request.POST:
    #         return self.handle_game_form(game_form)
    #
    #     if 'submit_court' in request.POST and court_form.is_valid():
    #         court_form.save()
    #         logger.info("Court created successfully.")
    #         return redirect('day')
    #
    #     if 'submit_category' in request.POST and category_form.is_valid():
    #         category_form.save()
    #         logger.info("Category created successfully.")
    #         return redirect('day')
    #
    #     return self.form_invalid_response(game_form, court_form, category_form)
    #
    # def handle_game_form(self, game_form):
    #     if game_form.is_valid():
    #         game = self.save_game(game_form)
    #         if game.group:
    #             self.handle_recurring_events(game)
    #         return redirect('day')
    #     else:
    #         logger.error(f"Game form is invalid. Errors: {game_form.errors}")
    #         return self.form_invalid_response(game_form)
    #
    # def save_game(self, game_form):
    #     game = game_form.save(commit=False)
    #     game.creator = self.request.user
    #     game.save()
    #     logger.info(f"Game saved with id: {game.game_id}")
    #     return game
    #
    # def handle_recurring_events(self, game):
    #     if not game.group:
    #         print(f"Game {game.name} does not have a group set for recurrence.")
    #         return
    #
    #     recurrence_type = game.group.recurrence_type
    #     delta = self.get_recurrence_delta(recurrence_type)
    #
    #     if delta is None:
    #         print(f"Delta is None: {recurrence_type}")
    #         return
    #
    #     if delta:
    #         # Konwersja end_date na datetime z godziną 23:59
    #         recurrence_end_datetime = datetime.combine(game.group.end_date, time(23, 59))
    #         recurrence_end_datetime = make_aware(recurrence_end_datetime)
    #         current_start_date = game.start_date_and_time + delta
    #         current_end_date = game.end_date_and_time + delta
    #
    #         print(f"Creating recurring events for game {game.name} with recurrence type {recurrence_type}.")
    #         print(f"Initial event start: {game.start_date_and_time}, end: {game.end_date_and_time}")
    #
    #         while current_start_date <= recurrence_end_datetime:
    #             print(f"Creating event on {current_start_date} to {current_end_date}")
    #             Game.objects.create(
    #                 name=game.name,
    #                 category=game.category,
    #                 court=game.court,
    #                 start_date_and_time=current_start_date,
    #                 end_date_and_time=current_end_date,
    #                 group=game.group,
    #                 creator=self.request.user
    #             )
    #             current_start_date += delta
    #             current_end_date += delta
    #
    # def get_recurrence_delta(self, recurrence_type):
    #     if recurrence_type == 'daily':
    #         return timedelta(days=1)
    #     elif recurrence_type == 'weekly':
    #         return timedelta(weeks=1)
    #     elif recurrence_type == 'biweekly':
    #         return timedelta(weeks=2)
    #     elif recurrence_type == 'monthly':
    #         return relativedelta(months=1)
    #     else:
    #         print(f"Unrecognized recurrence type: {recurrence_type}")
    #     return None
    #
    # def form_invalid_response(self, game_form, court_form=None, category_form=None):
    #     context = self.get_context_data()
    #     context.update({'game_form': game_form})
    #     if self.request.user.is_staff:
    #         context.update({
    #             'court_form': court_form or CourtForm(),
    #             'category_form': category_form or CategoryForm(),
    #         })
    #     logger.error("Form submission failed.")
    #     return render(self.request, self.template_name, context)


class WeekView(LoginRequiredMixin, TemplateView):
    template_name = 'week.html'