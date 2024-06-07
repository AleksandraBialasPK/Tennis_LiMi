from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role
from django.contrib import messages
from django.contrib.auth.signals import user_logged_out


@receiver(post_migrate)
def insert_initial_data(sender, **kwargs):
    if sender.name == 'Tennis':
        roles = ['regular', 'admin']
        for role_name in roles:
            Role.objects.get_or_create(role_name=role_name)


@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    messages.success(request, "You have been logged out.")