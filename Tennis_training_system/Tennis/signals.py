from django.db.models.signals import post_migrate, pre_save, post_save
from django.dispatch import receiver
from .models import Role, Court
from geopy.geocoders import Nominatim
from .utils import recalculate_travel_time_for_games


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

@receiver(post_save, sender=Court)
def handle_court_update(sender, instance, **kwargs):
    """
    Signal to detect when a court's latitude or longitude changes.
    If latitude/longitude has changed, trigger travel time recalculation for affected games.
    """
    # Fetch the previous state of the court (if it already exists)
    if instance.pk:
        try:
            old_instance = Court.objects.get(pk=instance.pk)
        except Court.DoesNotExist:
            old_instance = None

        if old_instance:
            # Check if latitude or longitude has changed
            if old_instance.latitude != instance.latitude or old_instance.longitude != instance.longitude:
                # Latitude/Longitude has changed, trigger travel time recalculation
                recalculate_travel_time_for_games(instance)
