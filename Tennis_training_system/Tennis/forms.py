from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Game, Category, Court, RecurringGroup



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2', 'profile_picture')

class EventForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['category', 'court', 'start_date_and_time', 'end_date_and_time', 'group']