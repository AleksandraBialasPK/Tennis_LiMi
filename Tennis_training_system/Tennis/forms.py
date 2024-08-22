from urllib import request

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Game, Category, Court, RecurringGroup, RECURRENCE_CHOICES
from django.contrib.auth.forms import AuthenticationForm
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from django.core.validators import EmailValidator
import logging

logger = logging.getLogger(__name__)


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class ParticipantsWidget(ModelSelect2MultipleWidget):
    search_fields = [
        'username__icontains',
        'email__icontains',
    ]


class GameForm(forms.ModelForm):
    recurrence_type = forms.ChoiceField(choices=RECURRENCE_CHOICES, required=False, label="Recurrence Type")
    end_date_of_recurrence = forms.DateField(required=False, label="End Date of Recurrence",
                                             widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Game
        fields = ['name', 'category', 'start_date_and_time', 'end_date_and_time', 'court', 'participants', 'recurrence_type']
        widgets = {
            'start_date_and_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date_and_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Category")
    court = forms.ModelChoiceField(queryset=Court.objects.all(), label="Court")
    participants = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.all(), widget=ParticipantsWidget,
                                                  label="Participants")

    def save(self, commit=True):
        instance = super(GameForm, self).save(commit=False)
        recurrence_type = self.cleaned_data.get('recurrence_type', None)
        end_date_of_recurrence = self.cleaned_data.get('end_date_of_recurrence', None)

        logger.info(f"Saving game: {instance.name}")
        logger.info(f"Recurrence type: {recurrence_type}")

        if recurrence_type and end_date_of_recurrence:
            group = RecurringGroup.objects.create(
                recurrence_type=recurrence_type,
                start_date=instance.start_date_and_time,
                end_date=end_date_of_recurrence
            )
            logger.info(f"Recurring group created with ID: {group.group_id}")
            instance.group = group

        if commit:
            instance.save()
            self.save_m2m()
            logger.info(f"Game saved with ID: {instance.id}")
        return instance


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class CourtForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = ['name', 'building_number', 'street', 'postal_code', 'city', 'country']


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password1', 'password2']


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

