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
            'name', 'category__name', 'start_date_and_time', 'end_date_and_time'
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


class WeekView(LoginRequiredMixin, TemplateView):
    template_name = 'week.html'