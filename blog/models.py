from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from CampaignNova.settings import base as settings


class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Blog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blogs"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)  # Add slug field
    content = RichTextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="blogs"
    )
    tags = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="blogs/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:  # Generate slug only if it’s empty
            self.slug = slugify(self.title)  # Create slug from title
        super().save(*args, **kwargs)  # Call the original save method


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_comments"
    )  # Changed related_name here
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
