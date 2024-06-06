from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role

@receiver(post_migrate)
def insert_initial_data(sender, **kwargs):
    if sender.name == 'Tennis':
        roles = ['regular', 'admin']
        for role_name in roles:
            Role.objects.get_or_create(role_name=role_name)