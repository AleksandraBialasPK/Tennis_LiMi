from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator

from Tennis_training_system import settings
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _
from .forms import EmailAuthenticationForm,  GameForm, CourtForm, CategoryForm
from django.views.generic import FormView, ListView, TemplateView, CreateView, View
from .models import Game, Participant, Category, Court
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


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

    def get_queryset(self):
        return Game.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.get_queryset()
        context['game_form'] = GameForm()
        if self.request.user.is_staff:
            context['court_form'] = CourtForm()
            context['category_form'] = CategoryForm()
        return context

    def post(self, request, *args, **kwargs):
        game_form = GameForm(request, request.POST)
        court_form = CourtForm(request.POST)
        category_form = CategoryForm(request.POST)

        if 'submit_game' in request.POST and game_form.is_valid():
            game_form.save()
            return redirect('day')

        if 'submit_court' in request.POST and court_form.is_valid():
            court_form.save()
            return redirect('day')

        if 'submit_category' in request.POST and category_form.is_valid():
            category_form.save()
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
        return render(request, self.template_name, context)


class WeekView(LoginRequiredMixin, TemplateView):
    template_name = 'week.html'

