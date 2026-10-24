from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import OrganizationProfile, User


class OrganizationProfileInline(admin.StackedInline):
    model = OrganizationProfile
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [OrganizationProfileInline]


admin.site.register(User, CustomUserAdmin)
admin.site.register(OrganizationProfile)