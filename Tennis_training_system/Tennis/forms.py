from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Game, Category, Court, RecurringGroup, RECURRENCE_CHOICES
from django.contrib.auth.forms import AuthenticationForm
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from django.core.validators import EmailValidator


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class ParticipantsWidget(ModelSelect2MultipleWidget):
    search_fields = [
        'username__icontains',
        'email__icontains',
    ]


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name', 'category', 'start_date_and_time', 'end_date_and_time', 'court', 'participants', 'group']
        widgets = {
            'start_date_and_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date_and_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Category"
    )

    court = forms.ModelChoiceField(
        queryset=Court.objects.all(),
        label="Court"
    )

    participants = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=ParticipantsWidget,
        label="Participants",
    )

    group = forms.ChoiceField(
        choices=RECURRENCE_CHOICES,
        label="Recurrence"
    )


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

