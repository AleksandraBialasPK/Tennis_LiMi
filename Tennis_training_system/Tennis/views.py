from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django import forms
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {email}.")
                return redirect('day')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = EmailAuthenticationForm()

    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('day')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required(login_url='login')
def day(request):
    return render(request, "day.html")


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out!")
    return redirect('login')