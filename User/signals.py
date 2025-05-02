from django.db.models.signals import post_save
from django.dispatch import receiver

from User.models import CustomUser, CustomUserProfile


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        user_profile = CustomUserProfile.objects.create(user=instance)
        user_profile.is_public = True
        user_profile.user = instance
        user_profile.save()