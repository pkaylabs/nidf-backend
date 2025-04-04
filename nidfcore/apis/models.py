import random
import string
from django.utils import timezone
from datetime import timedelta

from django.db import models

from accounts.models import Church, District, Region, User
from nidfcore.utils.constants import (ApplicationStatus, ConstLists as CL, Frequency,
                                      NotificationChannel, ReportStatus, SupportType, Target)
from nidfcore.utils.services import send_sms


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
    support_type = models.CharField(max_length=20, choices=CL().support_types, default=SupportType.AID.value)
    type_of_church_project = models.CharField(max_length=50, choices=CL().church_project_types, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    amount_in_words = models.CharField(max_length=500, default='')
    estimated_project_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    project_location = models.CharField(max_length=500, default='')
    purpose = models.TextField(null=True, blank=True)
    phase = models.CharField(max_length=100, default='')
    description = models.TextField(null=True, blank=True) 
    status = models.CharField(max_length=25, default=ApplicationStatus.DRAFT.value, choices=CL.application_statuses)
    expected_completion_date = models.DateField(null=True, blank=True)
    is_emergency = models.BooleanField(default=False)

    # documents
    current_stage = models.FileField(upload_to='applications/current_stage/', null=True, blank=True)
    cost_estimate = models.FileField(upload_to='applications/cost_estimate/', null=True, blank=True)
    land_ownership = models.FileField(upload_to='applications/land_ownership/', null=True, blank=True)
    invoices = models.FileField(upload_to='applications/invoices/', null=True, blank=True)
    
    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_by')


    def get_disbursed_amount(self) -> float:
        '''Returns the total amount disbursed for the application'''
        return sum([disb.amount for disb in self.disbursement_set.all()])
    
    def get_repayment_amount(self) -> float:
        '''Returns the total amount repaid for the application'''
        return sum([rep.amount for rep in self.repayment_set.all()])
    
    def notify_applicant(self, started=False, submitted=False, approved=False, rejected=False):
        '''Notify the applicant that the application is received|approved|rejected'''
        started_msg = f"Greetings from the NIDF Team.\n\nWe just realized you started an application. Your application ID is {self.application_id}. Please note that you have to provide all the required information in order to be considered. Thank you.\n\nThe NIDF Team."
        submitted_msg = f"Thank you for submitting your application. Your application ID is {self.application_id}. We will get back to you as soon as possible.\n\nThe NIDF Team."
        approved_msg = f"Congratulations from the NIDF Team.\n\nWe just approved your application for funding. Your application ID is {self.application_id}. Thank you.\n\nThe NIDF Team."
        rejected_msg = f"Greetings from the NIDF Team.\n\nWe regret to inform you that your application with id ({self.application_id}) has been rejected.\nYou may try another application at a later date. Thank you.\n\nThe NIDF Team."
        phone = self.church.pastor_phone
        phone2 = self.church.church_phone
        if started:
            msg = started_msg
        elif submitted:
            msg = submitted_msg
        elif approved:
            msg = approved_msg
        elif rejected:
            msg = rejected_msg
        else:
            # message defaults to started message
            msg = started_msg
        send_sms(msg, [phone, phone2])

    def __str__(self):
        return self.application_id


class Repayment(models.Model):
    '''Repayment model'''

    def generate_repayment_id() -> str:
        '''Generates a unique id for repayment record'''
        sub = 'NIDF-RR-'
        return sub + ''.join(random.choices(string.digits, k=7))

    repayment_id = models.CharField(max_length=15, default=generate_repayment_id, unique=True)
    application = models.ForeignKey(Application, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    payment_reference = models.CharField(max_length=50, default='')
    date_paid = models.DateField()
    proof_of_payment = models.FileField(upload_to='repayments/')
    status = models.CharField(max_length=15, default=ApplicationStatus.PENDING.value)

    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='creator')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='updator')

    def __str__(self):
        return f"{self.repayment_id} - {self.amount}"
    
class ProgressReport(models.Model):
    '''Progress report model'''
    def generate_report_id() -> str:
        '''Generates a unique id for progress report'''
        sub = 'NIDF-PR-'
        return sub + ''.join(random.choices(string.digits, k=7))
    
    report_id = models.CharField(max_length=15, default=generate_report_id, unique=True)
    application = models.ForeignKey(Application, on_delete=models.PROTECT)
    progress_description = models.TextField()
    proof_of_progress = models.FileField(upload_to='progress/')
    status = models.CharField(max_length=15, default=ReportStatus.PENDING.value, choices=CL.report_statuses)
    activity_completed = models.BooleanField(default=False)

    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='progress')

    def __str__(self):
        return self.report_id
    

class Disbursement(models.Model):
    '''Disbursement model'''

    def generate_disbursement_id() -> str:
        '''Generates a unique id for disbursement record'''
        sub = 'NIDF-DB-'
        return sub + ''.join(random.choices(string.digits, k=7))

    disbursement_id = models.CharField(max_length=15, default=generate_disbursement_id, unique=True)
    application = models.ForeignKey(Application, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    payment_reference = models.CharField(max_length=50, default='')
    date_paid = models.DateField()
    proof_of_payment = models.FileField(upload_to='disbursments/')
    status = models.CharField(max_length=15, default=ApplicationStatus.PENDING.value)

    # bank details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)

    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)

    def notify_applicant_church(self):
        '''notify the church that disbursement has been made'''
        msg = f"Greetings from the NIDF Team.\n\nWe just disbursed {self.amount} to your church. Your application ID is {self.application.application_id}. Thank you.\n\nThe NIDF Team."
        phone = self.application.church.pastor_phone
        send_sms(msg, [phone])

    def __str__(self):
        return f"{self.disbursement_id} - {self.amount}"
    

class Notification(models.Model):
    '''Notification model'''
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_scheduled = models.BooleanField(default=False)
    schedule_start_date = models.DateTimeField(null=True, blank=True)
    schedule_start_end = models.DateTimeField(null=True, blank=True)
    schedule_frequency = models.CharField(max_length=20, default=Frequency.WEEKLY.value)
    target = models.CharField(max_length=20, choices=CL().notification_targets, default=Target.ALL.value)
    attachment = models.FileField(upload_to='notifications/', null=True, blank=True)
    # stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    broadcasted_at = models.DateTimeField(null=True, blank=True)
    broadcasted_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='created_by')

    def can_broadcast(self) -> bool:
        '''Checks if the notification can be broadcasted'''
        if not self.is_scheduled:
            return False

        if self.schedule_start_date and self.schedule_start_end:
            now = timezone.now()

            # Normalize the time to only include hour and minute
            now_time = now.replace(second=0, microsecond=0)
            start_time = self.schedule_start_date.replace(second=0, microsecond=0)

            # Check if the current time is within the start and end range
            if not (self.schedule_start_date <= now <= self.schedule_start_end):
                return False

            # Calculate if the current datetime matches the exact frequency
            if self.schedule_frequency == Frequency.DAILY.value:
                # Check if the time matches the start date's time
                return now_time.time() == start_time.time()

            elif self.schedule_frequency == Frequency.WEEKLY.value:
                # Check if the day of the week and time match
                return (
                    now.weekday() == self.schedule_start_date.weekday() and
                    now_time.time() == start_time.time()
                )

            elif self.schedule_frequency == Frequency.FORTNIGHTLY.value:
                # Check if the current date is exactly 14 days apart from the start date
                delta_days = (now.date() - self.schedule_start_date.date()).days
                return (
                    delta_days % 14 == 0 and
                    now_time.time() == start_time.time()
                )

            elif self.schedule_frequency == Frequency.MONTHLY.value:
                # Check if the day of the month and time match
                return (
                    now.day == self.schedule_start_date.day and
                    now_time.time() == start_time.time()
                )

        return False
    
    
    def broadcast(self, user: User = None, channel: str = NotificationChannel.SMS.value):
        '''Broadcasts the notification to a user'''
        if self.target == Target.ALL.value:
            # get all the phones for the users
            phones = [u.phone for u in User.objects.all()]
        elif self.target == Target.CHURCH.value:
            # get all the phones for the church and the pastor
            churches = Church.objects.all()
            phones = [u.pastor_phone for u in churches].extend([u.church_phone for u in churches])
        elif self.target == Target.REGION.value:
            # get all the phones for the region and the overseer
            regions = Region.objects.all()
            phones = [u.phone for u in regions].extend([u.overseer_phone for u in regions])
        elif self.target == Target.DISTRICT.value:
            # get all the phones for the district and the overseer
            districts = District.objects.all()
            phones = [u.phone for u in districts].extend([u.overseer_phone for u in districts])
        else:
            # get the phone for the user
            if not user:
                return
            phones = [user.phone]

        # send the notification to the phones
        msg = f"{self.title}\n\n{self.message}"
        send_sms(recipients=phones, message=msg)

        self.broadcasted_by = user
        self.broadcasted_at = timezone.now()
        self.save()

        return True

    def __str__(self):
        return self.title