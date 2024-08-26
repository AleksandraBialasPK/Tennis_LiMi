from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_migrate
import logging
logger = logging.getLogger(__name__)

# Role choices
ROLE_CHOICES = [
    ('regular', 'regular'),
    ('admin', 'admin'),
]

# Status choices for CreateGameRequest and ParticipantRequest
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]

# Recurrence type choices for RecurringGroup
RECURRENCE_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('biweekly', 'Biweekly'),
    ('monthly', 'Monthly'),
    (None, 'None'),
]


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.role_name

    @classmethod
    def get_default_role(cls):
        return cls.objects.get_or_create(role_name='regular')[0]


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=Role.get_default_role)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7)

    def __str__(self):
        return self.name


class Court(models.Model):
    court_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    building_number = models.CharField(max_length=10)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RecurringGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    recurrence_type = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"Group {self.group_id}"


class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, default='Tennis game')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_date_and_time = models.DateTimeField()
    end_date_and_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(RecurringGroup, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Game {self.game_id} by {self.creator}"


class CreateGameRequest(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='create_requests')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    start_date_and_time = models.DateTimeField()
    end_date_and_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    group = models.ForeignKey(RecurringGroup, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Request by {self.sender}"


class ParticipantRequest(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='participant_requests')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Request by {self.sender} for game {self.game}"


class ParticipantReceiver(models.Model):
    request = models.ForeignKey(CreateGameRequest, on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Receiver {self.receiver} for request {self.request}"


class Participant(models.Model):
    participant_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_trainer = models.BooleanField(default=False)

    def __str__(self):
        return f"Participant {self.user} in game {self.game}"
