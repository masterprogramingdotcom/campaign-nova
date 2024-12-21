from django.contrib import admin

from .models import Profile, User


class UserAdmin(admin.ModelAdmin):
    list_display = ("mobile_number", "is_active", "is_staff", "is_superuser")


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
