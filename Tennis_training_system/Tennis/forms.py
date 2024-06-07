from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Game, Category, Court, RecurringGroup
from django.contrib.auth.forms import AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')


class EventForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['category', 'court', 'start_date_and_time', 'end_date_and_time', 'group']


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

