'''
This module contains the models for the accounts application.
It includes the User, Church, Region, and District models.
These models are used to store information about the users 
and their respective divisional profiles.

'''

from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from nidfcore.utils.constants import ApplicationStatus, ChurchType, UserType

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

    def get_church_logo(self) -> str:
        '''Returns the church logo'''
        if self.church_profile and self.church_profile.church_logo:
            return self.church_profile.church_logo.url
        return None

    def __str__(self):
        return self.name

class OTP(models.Model):
    '''One Time Password model'''
    phone = models.CharField(max_length=12)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self) -> bool:
        '''Returns True if the OTP is expired'''
        return (self.created_at + timedelta(minutes=30)) < timezone.now()
    
    def send_otp(self) -> None:
        '''Send the OTP to the user'''
        from nidfcore.utils.services import send_sms
        message = f"Welcome to the DL NIDF Ghana platform.\n\nYour OTP is {self.otp}.\n\nPlease do not share this with anyone."
        send_sms(message, [self.phone])


    def __str__(self):
        return self.phone + ' - ' + str(self.otp)


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
    church_logo = models.ImageField(upload_to='churches/logos/', null=True, blank=True)
    church_type = models.CharField(max_length=20, default=ChurchType.LOCATION.value)

    # heirarchy
    district = models.ForeignKey('District', on_delete=models.CASCADE, null=True, blank=True)

    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    def get_amount_received(self) -> float:
        '''Returns the total amount received by the church in the form of disbursements'''
        return sum([app.get_disbursed_amount() for app in self.application_set.all()])
    
    def get_amount_repaid(self) -> float:
        '''Returns the total amount repaid by the church in the form of repayments'''
        return sum([app.get_repayment_amount() for app in self.application_set.all() if app.status == ApplicationStatus.APPROVED.value])
    
    def get_arrears(self) -> float:
        '''Returns the total arrears of the church'''
        return self.get_amount_received() - self.get_amount_repaid()
    
    def get_repaid_percentage(self) -> float:
        '''Returns the percentage of the total amount received that has been repaid'''
        total_received = self.get_amount_received()
        total_repaid = self.get_amount_repaid()
        if total_received == 0:
            return 0
        return (total_repaid / total_received) * 100
    
    def get_last_repayment_date(self) -> any:
        '''Returns the last repayment date'''
        last_application = self.application_set.all().order_by('-updated_at').first()
        last_payment = last_application.repayment_set.all().order_by('-date_paid').first() if last_application else None
        if last_payment:
            last_payment_date = last_payment.date_paid
            # convert to string format: dd/mm/yyyy
            last_payment_date = last_payment_date.strftime('%d/%m/%Y')
            return last_payment_date
        return "None"
    
    def get_next_due_date(self) -> str:
        '''Returns the next due date for repayment'''
        # it should be a month from the last repayment date
        last_application = self.application_set.all().order_by('-updated_at').first()
        last_payment = last_application.repayment_set.all().order_by('-date_paid').first() if last_application else None
        if last_payment:
            last_repayment_date = last_payment.date_paid
        else:
            last_repayment_date = last_application.created_at if last_application else timezone.now()
        return last_repayment_date + timedelta(days=30)

    def __str__(self):
        return self.name
    

class Region(models.Model):
    '''Region model'''
    name = models.CharField(max_length=255, unique=True)
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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def districts(self) -> int:
        '''Returns the districts in the region'''
        districts = District.objects.filter(region=self).count()
        return districts
    
    @property
    def churches(self) -> int:
        '''Returns the churches in the region'''
        churches = Church.objects.filter(district__region=self).count()
        return churches
    
    @property
    def created_by_user(self) -> str:
        '''Returns the user that created the region'''
        if self.created_by:
            return self.created_by.name
        return "Admin User"

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

    # region
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True, blank=True)

    # district details
    phone = models.CharField(max_length=12)
    email = models.EmailField()

    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name