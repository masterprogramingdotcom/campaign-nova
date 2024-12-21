from CampaignNova.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-stage-+p%rziio8*k4l05-v^3)zr+t+$13!$7-#v!2s^hi^6)s+i*rx("

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "marlin_ai_stage",
        "USER": "marlin_user",
        "PASSWORD": "Welcome@12",
        "HOST": "localhost",
        "PORT": "5432",  # Default PostgreSQL port
    }
}

# export DJANGO_SETTINGS_MODULE=CampaignNova.settings.stage_settings
