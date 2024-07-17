from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Game, Category, Court, RecurringGroup
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Game


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['category', 'start_date_and_time', 'end_date_and_time', 'court']
        widgets = {
            'start_date_and_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date_and_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a category",
        label="Category"
    )


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

