from datetime import datetime, timezone

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return f'{self.email} <-> {self.username}'
class CustomUserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    is_public = models.BooleanField(default=False)
    private_share_token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    private_token_expires_at = models.DateTimeField(blank=True, null=True)
    def generate_private_token(self, days=7):
        import secrets
        from datetime import timedelta
        from django.utils import timezone
        self.private_share_token = secrets.token_urlsafe(32)
        self.private_token_expires_at = timezone.now()+timedelta(days=days)
        self.save()
    def __str__(self):
        return f"profile of {self.user.username}"
class Trip(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    place = models.CharField(max_length=255)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField( null=False)
    date = models.DateField()
    note = models.TextField(blank=True)
    def __str__(self):
        return f'{self.user.email} -> {self.place}'
class TripPhoto(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='photos')
    image_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)