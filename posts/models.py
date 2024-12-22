from ckeditor.fields import RichTextField
from django.db import models

from CampaignNova.settings import base as settings


class SocialMediaAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_account",
    )
    twitter = models.CharField(max_length=255, blank=True, null=True)
    twitter_secret = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=255)  # New title field
    content = RichTextField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    shared_on_twitter = models.BooleanField(default=False)
    shared_on_facebook = models.BooleanField(default=False)
    shared_on_instagram = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.mobile_number
