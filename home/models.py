from ckeditor.fields import RichTextField
from django.db import models

from CampaignNova.settings import base as settings


class WebSetup(models.Model):
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    logo_white = models.ImageField(upload_to="logos/white/")
    logo_black = models.ImageField(upload_to="logos/black/")
    description = RichTextField()  # Changed to RichTextField
    fb_link = models.URLField(blank=True, null=True)
    x_link = models.URLField(blank=True, null=True)
    insta_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    whatsapp_link = models.URLField(blank=True, null=True)
    company_all_rights = models.CharField(max_length=255)

    def __str__(self):
        return self.email  # Or any other field to represent the company


class Contact(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    comments = RichTextField()  # Changed to RichTextField for rich text comments

    def __str__(self):
        return f"{self.full_name} {self.phone}"


class Location(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="location",
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    system_identifier = models.CharField(
        max_length=255
    )  # e.g., IP address or system type
    timestamp = models.DateTimeField(
        auto_now_add=True
    )  # To track when the location was saved

    def save(self, *args, **kwargs):
        # Only save with user if the user is authenticated
        if self.user and not self.user.is_authenticated:
            # Clear the user field if the user is not authenticated
            self.user = None

        # Save the location instance
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("user", "latitude", "longitude", "system_identifier")
