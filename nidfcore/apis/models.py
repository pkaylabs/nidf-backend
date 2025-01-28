from django.db import models
import random
import string

from accounts.models import User, Church
from nidfcore.utils.constants import ApplicationStatus, ConstLists, SupportType


class Application(models.Model):
    '''Application model'''

    def generate_application_id() -> str:
        '''Generates a unique application id'''
        sub = 'NIDF-AP-'
        return sub + ''.join(random.choices(string.digits, k=7))

    application_id = models.CharField(max_length=15, default=generate_application_id, unique=True)

    # CHURCH DETAILS
    church = models.ForeignKey(Church, on_delete=models.CASCADE, null=True, blank=True)
    avg_service_attendance = models.IntegerField(default=0)
    avg_monthly_income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    avg_monthly_contributions = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    avg_monthly_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    available_funds_for_project = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    # SUPPORT DETAILS
    support_type = models.CharField(max_length=20, choices=ConstLists().support_types, default=SupportType.AID.value)
    type_of_church_project = models.CharField(max_length=50, choices=ConstLists().church_project_types)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    amount_in_words = models.CharField(max_length=500, default='')
    estimated_project_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    project_location = models.CharField(max_length=500)
    purpose = models.TextField()
    phase = models.CharField(max_length=100)
    description = models.TextField() 
    status = models.CharField(max_length=20, default=ApplicationStatus.DRAFT.value)
    
    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.application_id
