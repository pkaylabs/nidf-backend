'''
This module contains the models for the accounts application.
It includes the User, Church, Region, and District models.
These models are used to store information about the users 
and their respective divisional profiles.

'''

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from nidfcore.utils.constants import UserType

from .manager import AccountManager


class User(AbstractBaseUser, PermissionsMixin):
    '''Custom User model for the application'''
    email = models.EmailField(max_length=50, unique=True)
    phone = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, default=UserType.CHURCH_USER.value)

    church_profile = models.OneToOneField('Church', on_delete=models.CASCADE, null=True, blank=True)

    deleted = models.BooleanField(default=False)  # Soft delete
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'name']

    def __str__(self):
        return self.name
    

class Church(models.Model):
    '''Church profile model'''
    name = models.CharField(max_length=255)
    address = models.TextField()

    # administator details
    pastor_name = models.CharField(max_length=255)
    pastor_phone = models.CharField(max_length=12)
    pastor_email = models.EmailField()

    # church details
    church_phone = models.CharField(max_length=12)
    church_email = models.EmailField()
    church_logo = models.ImageField(upload_to='churches/logos/')

    # heirarchy
    district = models.ForeignKey('District', on_delete=models.CASCADE)
    region = models.ForeignKey('Region', on_delete=models.CASCADE)

    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    

class Region(models.Model):
    '''Region model'''
    name = models.CharField(max_length=255)
    location = models.TextField()

    # overseer details
    overseer_name = models.CharField(max_length=255)
    overseer_phone = models.CharField(max_length=12)
    overseer_email = models.EmailField()

    # region details
    phone = models.CharField(max_length=12)
    email = models.EmailField()

    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class District(models.Model):
    '''District model'''
    name = models.CharField(max_length=255)
    location = models.TextField()

    # overseer details
    overseer_name = models.CharField(max_length=255)
    overseer_phone = models.CharField(max_length=12)
    overseer_email = models.EmailField()

    # region details
    phone = models.CharField(max_length=12)
    email = models.EmailField()

    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name