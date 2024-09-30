from django.db.models.signals import post_migrate, pre_save
from django.dispatch import receiver
from .models import Role, Court
from geopy.geocoders import Nominatim

@receiver(post_migrate)
def insert_initial_data(sender, **kwargs):
    if sender.name == 'Tennis':
        roles = ['regular', 'admin']
        for role_name in roles:
            Role.objects.get_or_create(role_name=role_name)


@receiver(pre_save, sender=Court)
def set_lat_lon(sender, instance, **kwargs):
    geolocator = Nominatim(user_agent="Tennis")

    if instance.pk:
        old_instance = Court.objects.get(pk=instance.pk)
        address_fields = ['building_number', 'street', 'city', 'postal_code', 'country']
        if any(getattr(old_instance, field) != getattr(instance, field) for field in address_fields):
            address = f"{instance.building_number} {instance.street}, {instance.city}, {instance.postal_code}, {instance.country}"
            location = geolocator.geocode(address)
            if location:
                instance.latitude = location.latitude
                instance.longitude = location.longitude

    if not instance.latitude or not instance.longitude:
        address = f"{instance.building_number} {instance.street}, {instance.city}, {instance.postal_code}, {instance.country}"
        location = geolocator.geocode(address)
        if location:
            instance.latitude = location.latitude
            instance.longitude = location.longitude
        else:
            print(f"Error: Geolocation not found for address: {address}")
