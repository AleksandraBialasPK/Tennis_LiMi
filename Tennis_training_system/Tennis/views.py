from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.views.generic import FormView, TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _
from .forms import EmailAuthenticationForm,  GameForm
from .models import Game
from datetime import datetime, date
from django.views.generic import ListView


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('day')

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


class DayView(ListView):
    model = Game
    template_name = 'day.html'  # Nazwa szablonu HTML dla listy wydarzeń

    def get_queryset(self):
        return Game.objects.all()  # Pobieramy wszystkie wydarzenia

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.get_queryset()  # Przekazujemy listę wydarzeń do kontekstu szablonu
        return context


class CreateEventView(CreateView):
    model = Game
    form_class = GameForm
    template_name = 'day.html'
    success_url = reverse_lazy('day')

    def form_valid(self, form):
        event = form.save(commit=False)
        event.creator = self.request.user
        event.save()
        return super().form_valid(form)



class WeekView(LoginRequiredMixin, TemplateView):
    template_name = 'week.html'

