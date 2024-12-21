from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile, User


@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create or update the Profile whenever a User is created or updated.
    """
    if created:
        # Create a profile for the new user
        Profile.objects.get_or_create(user=instance)
    else:
        # Save the profile if the user is updated
        instance.profile.save()
