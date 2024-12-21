from django.db import models


# Define user roles using TextChoices for better clarity and management
class UserRole(models.TextChoices):
    VENDOR = "Vendor", ("Vendor")
    CUSTOMER = "Customer", ("Customer")
