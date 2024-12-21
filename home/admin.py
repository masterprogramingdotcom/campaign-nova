from django.contrib import admin

from home.models import Contact, Location, WebSetup

# Register your models here.

admin.site.register(Contact)
admin.site.register(WebSetup)
admin.site.register(Location)
