from django.contrib import admin
from .models import *

# Application
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'church__name', 'amount', 'status', 'created_at',)
    list_filter = ('status', 'church',)
    search_fields = ('application_id', 'church__name',)

# Repayment
@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ('repayment_id', 'application', 'amount', 'status', 'created_at',)
    list_filter = ('status',)
    search_fields = ('repayment_id', 'application_application_id',)

# Progress Report
@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'status', 'created_at',)
    list_filter = ('status',)
    search_fields = ('report_id',)