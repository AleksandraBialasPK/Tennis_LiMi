from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _
from .forms import EmailAuthenticationForm


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


@login_required(login_url='login')
def day(request):
    return render(request, "day.html")


@login_required(login_url='login')
def week(request):
    return render(request, "week.html")

