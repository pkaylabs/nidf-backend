from django.contrib import admin

from .models import *

admin.site.site_header = 'NIDF Admin Portal'

# user
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'church_profile__name','is_staff', 'is_superuser')
    search_fields = ('name', 'email', 'phone',)
