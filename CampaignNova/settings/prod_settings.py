from CampaignNova.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-prod-+p%rziio8*k4l05-v^3)zr+t+$13!$7-#v!2s^hi^6)s+i*rx("

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["CampaignNova.com", "www.CampaignNova.com", "3.110.91.144"]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "CampaignNova_prod",
#         "USER": "guwnwala_user",
#         "PASSWORD": "Welcome@12",
#         "HOST": "localhost",
#         "PORT": "5432",  # Default PostgreSQL port
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "prod_db.sqlite3",
    }
}


CSRF_TRUSTED_ORIGINS = [
    "https://CampaignNova.com",
    "https://www.CampaignNova.com",
]

CORS_ALLOWED_ORIGINS = [
    "https://CampaignNova.com",
    "https://www.CampaignNova.com",
]

# export DJANGO_SETTINGS_MODULE=CampaignNova.settings.prod_settings
