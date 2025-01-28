from django.contrib import admin

from .models import *

admin.site.site_header = 'NIDF Admin Portal'

# user
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'church_profile__name','is_staff', 'is_superuser')
    search_fields = ('name', 'email', 'phone',)


# church
@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ('name', 'pastor_name', 'location', 'district__name')
    search_fields = ('name', 'pastor_name', 'district__name',)

# district
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'overseer_name',)
    search_fields = ('name', 'location',)

# region
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'overseer_name',)
    search_fields = ('name', 'location',)