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
from django.views.generic.edit import CreateView
from datetime import timedelta, datetime, date, time
from django.utils import timezone
from dateutil.relativedelta import relativedelta
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


class DayView(LoginRequiredMixin, ListView):
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

    def post(self, request, *args, **kwargs):
        logger.info("Received POST request.")
        game_form = GameForm(request.POST)
        court_form = CourtForm(request.POST)
        category_form = CategoryForm(request.POST)

        if 'submit_game' in request.POST:
            return self.handle_game_form(game_form)

        if 'submit_court' in request.POST and court_form.is_valid():
            court_form.save()
            logger.info("Court created successfully.")
            return redirect('day')

        if 'submit_category' in request.POST and category_form.is_valid():
            category_form.save()
            logger.info("Category created successfully.")
            return redirect('day')

        return self.form_invalid_response(game_form, court_form, category_form)

    def handle_game_form(self, game_form):
        if game_form.is_valid():
            game = self.save_game(game_form)
            if game.group:
                self.handle_recurring_events(game)
            return redirect('day')
        else:
            logger.error(f"Game form is invalid. Errors: {game_form.errors}")
            return self.form_invalid_response(game_form)

    def save_game(self, game_form):
        game = game_form.save(commit=False)
        game.creator = self.request.user
        game.save()
        logger.info(f"Game saved with id: {game.game_id}")
        return game

    def handle_recurring_events(self, game):
        if not game.group:
            print(f"Game {game.name} does not have a group set for recurrence.")
            return

        recurrence_type = game.group.recurrence_type
        delta = self.get_recurrence_delta(recurrence_type)

        if delta is None:
            print(f"Delta is None: {recurrence_type}")
            return

        if delta:
            # Konwersja end_date na datetime z godziną 23:59
            recurrence_end_datetime = datetime.combine(game.group.end_date, time(23, 59))
            recurrence_end_datetime = make_aware(recurrence_end_datetime)
            current_start_date = game.start_date_and_time + delta
            current_end_date = game.end_date_and_time + delta

            print(f"Creating recurring events for game {game.name} with recurrence type {recurrence_type}.")
            print(f"Initial event start: {game.start_date_and_time}, end: {game.end_date_and_time}")

            while current_start_date <= recurrence_end_datetime:
                print(f"Creating event on {current_start_date} to {current_end_date}")
                Game.objects.create(
                    name=game.name,
                    category=game.category,
                    court=game.court,
                    start_date_and_time=current_start_date,
                    end_date_and_time=current_end_date,
                    group=game.group,
                    creator=self.request.user
                )
                current_start_date += delta
                current_end_date += delta

    def get_recurrence_delta(self, recurrence_type):
        if recurrence_type == 'daily':
            return timedelta(days=1)
        elif recurrence_type == 'weekly':
            return timedelta(weeks=1)
        elif recurrence_type == 'biweekly':
            return timedelta(weeks=2)
        elif recurrence_type == 'monthly':
            return relativedelta(months=1)
        else:
            print(f"Unrecognized recurrence type: {recurrence_type}")
        return None

    def form_invalid_response(self, game_form, court_form=None, category_form=None):
        context = self.get_context_data()
        context.update({'game_form': game_form})
        if self.request.user.is_staff:
            context.update({
                'court_form': court_form or CourtForm(),
                'category_form': category_form or CategoryForm(),
            })
        logger.error("Form submission failed.")
        return render(self.request, self.template_name, context)


class WeekView(LoginRequiredMixin, TemplateView):
    template_name = 'week.html'