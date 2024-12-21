from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.constants import UserRole
from CampaignNova.settings import base as settings


# Custom Manager for handling mobile number-based user authentication
class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        """Create and return a user with a mobile number and password."""
        if not mobile_number:
            raise ValueError(_("The mobile number field must be set"))
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(mobile_number, password, **extra_fields)

class User(AbstractBaseUser):
    # Mobile number as the unique identifier (username)
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.CharField(max_length=50, unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserRole.choices,  # Using TextChoices for user roles
        default=UserRole.CUSTOMER,  # Default to "Customer"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Required fields
    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = (
        []
    )  # No other required fields except the mobile number and password

    objects = CustomUserManager()

    def __str__(self):
        return self.mobile_number

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission.
        """
        return self.is_superuser

    def has_module_perms(self, app_label):
        """
        Return True if the user has permissions to view the app `app_label`.
        """
        return self.is_superuser

    @property
    def is_staff(self):
        """
        Return True if the user is a staff member (needed for admin access).
        """
        return self.is_superuser
    

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )
    otp = models.CharField(max_length=6, blank=True, null=True)  # Assuming 6-digit OTP
    mobile_verified = models.BooleanField(default=False)
    bio = RichTextField(blank=True, null=True)  # RichTextField for CKEditor
    aadhar_card = models.ImageField(
        upload_to="documents/aadhar/", null=True, blank=True
    )
    voter_id_card = models.ImageField(
        upload_to="documents/voter/", null=True, blank=True
    )
    pan_card = models.ImageField(upload_to="documents/pan/", null=True, blank=True)

    # New fields
    nationality = models.CharField(max_length=100, blank=True, null=True)
    experience = models.CharField(
        max_length=50, blank=True, null=True
    )  # Example: '10 Years'
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=(("Male", "Male"), ("Female", "Female"), ("Other", "Other")),
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.mobile_number

    # Optionally add a method to validate mobile number format
    def clean_mobile_number(self):
        import re

        # Assuming a 10-digit mobile number (you can adjust based on your requirement)
        if not re.match(r"^\+?[1-9]\d{1,14}$", self.user.mobile_number):
            raise ValueError("Invalid mobile number format")
