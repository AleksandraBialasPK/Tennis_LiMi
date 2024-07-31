from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _
from .forms import EmailAuthenticationForm,  GameForm, CourtForm, CategoryForm
from django.views.generic import FormView, ListView, TemplateView, CreateView, View
from .models import Game, RecurringGroup, Participant, Category, Court
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView
from datetime import timedelta
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
    form_class = GameForm
    success_url = "day/"
    context_object_name = 'events'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object_list = None

    def get_queryset(self):
        return Game.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.object_list
        context['game_form'] = GameForm()
        if self.request.user.is_staff:
            context['court_form'] = CourtForm()
            context['category_form'] = CategoryForm()
        return context

    def post(self, request, *args, **kwargs):
        logger.info("Received POST request.")
        self.object_list = self.get_queryset()

        game_form = GameForm(request.POST)
        court_form = CourtForm(request.POST)
        category_form = CategoryForm(request.POST)

        logger.info(f"Form data received: {request.POST}")

        if 'submit_game' in request.POST:
            if game_form.is_valid():
                logger.info("Game form is valid.")
                game = game_form.save(commit=False)
                game.creator = request.user
                logger.info(f"Creator before save: {game.creator}")
                game.save()
                logger.info(f"Game '{game.name}' created successfully.")

                if game.group:
                    recurrence_type = game.group.recurrence_type
                    start_date = game.start_date_and_time
                    end_date = game.end_date_and_time

                    delta = None
                    if recurrence_type == 'daily':
                        delta = timedelta(days=1)
                    elif recurrence_type == 'weekly':
                        delta = timedelta(weeks=1)
                    elif recurrence_type == 'biweekly':
                        delta = timedelta(weeks=2)
                    elif recurrence_type == 'monthly':
                        delta = relativedelta(months=1)

                    if delta:
                        current_start_date = start_date + delta
                        current_end_date = end_date + delta

                        while current_start_date <= game.group.end_date:
                            Game.objects.create(
                                name=game.name,
                                category=game.category,
                                court=game.court,
                                start_date_and_time=current_start_date,
                                end_date_and_time=current_end_date,
                                group=game.group,
                                creator=request.user
                            )
                            current_start_date += delta
                            current_end_date += delta

                return redirect('day')
            else:
                logger.error(f"Game form is invalid. Errors: {game_form.errors}")
                for field, errors in game_form.errors.items():
                    for error in errors:
                        logger.error(f"Error in {field}: {error}")

        if 'submit_court' in request.POST and court_form.is_valid():
            court_form.save()
            logger.info("Court created successfully.")
            return redirect('day')

        if 'submit_category' in request.POST and category_form.is_valid():
            category_form.save()
            logger.info("Category created successfully.")
            return redirect('day')

        context = self.get_context_data()
        context.update({
            'game_form': game_form,
        })
        if self.request.user.is_staff:
            context.update({
                'court_form': court_form,
                'category_form': category_form,
            })

        logger.error("Form submission failed.")
        return render(request, self.template_name, context)

# class DayView(LoginRequiredMixin, ListView):
#     model = Game
#     template_name = 'day.html'
#     form_class = GameForm
#     success_url = "day/"
#     context_object_name = 'events'
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.object_list = None
#
#     def get_queryset(self):
#         return Game.objects.all()
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['events'] = self.object_list
#         context['game_form'] = GameForm()
#         if self.request.user.is_staff:
#             context['court_form'] = CourtForm()
#             context['category_form'] = CategoryForm()
#         return context
#
#     def post(self, request, *args, **kwargs):
#         self.object_list = self.get_queryset()  # Ensure object_list is set
#
#         game_form = GameForm(request.POST)
#         court_form = CourtForm(request.POST)
#         category_form = CategoryForm(request.POST)
#
#         if 'submit_game' in request.POST and game_form.is_valid():
#             game = game_form.save(commit=False)
#             recurrence_type = game_form.cleaned_data['group']
#
#             if recurrence_type:
#                 start_date = game.start_date_and_time
#                 end_date = game.end_date_and_time
#
#                 group = RecurringGroup.objects.create(
#                     recurrence_type=recurrence_type,
#                     start_date=start_date,
#                     end_date=end_date
#                 )
#
#                 game.group = group
#                 game.save()
#
#                 delta = None
#                 if recurrence_type == 'daily':
#                     delta = timedelta(days=1)
#                 elif recurrence_type == 'weekly':
#                     delta = timedelta(weeks=1)
#                 elif recurrence_type == 'biweekly':
#                     delta = timedelta(weeks=2)
#                 elif recurrence_type == 'monthly':
#                     delta = relativedelta(months=1)
#
#                 if delta:
#                     current_start_date = start_date + delta
#                     current_end_date = end_date + delta
#
#                     while current_start_date <= group.end_date:
#                         Game.objects.create(
#                             name=game.name,
#                             category=game.category,
#                             court=game.court,
#                             creator=game.creator,
#                             start_date_and_time=current_start_date,
#                             end_date_and_time=current_end_date,
#                             group=group
#                         )
#                         current_start_date += delta
#                         current_end_date += delta
#
#             else:
#                 game.save()
#
#             return redirect('day')
#
#         if 'submit_court' in request.POST and court_form.is_valid():
#             court_form.save()
#             return redirect('day')
#
#         if 'submit_category' in request.POST and category_form.is_valid():
#             category_form.save()
#             return redirect('day')
#
#         context = self.get_context_data()
#         context.update({
#             'game_form': game_form,
#         })
#         if self.request.user.is_staff:
#             context.update({
#                 'court_form': court_form,
#                 'category_form': category_form,
#             })
#         return render(request, self.template_name, context)


class WeekView(LoginRequiredMixin, TemplateView):
    template_name = 'week.html'

