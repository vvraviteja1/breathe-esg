from django.db import models
from django.contrib.auth.models import User


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DataSource(models.Model):
    SOURCE_TYPES = [
        ('SAP_FLAT', 'SAP Flat File'),
        ('UTILITY_CSV', 'Utility Portal CSV'),
        ('TRAVEL_CSV', 'Travel Platform CSV'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('DONE', 'Done'),
        ('FAILED', 'Failed'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    errors_json = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.source_type} - {self.file_name}"


class EmissionRecord(models.Model):
    SCOPE_CHOICES = [
        (1, 'Scope 1'),
        (2, 'Scope 2'),
        (3, 'Scope 3'),
    ]
    REVIEW_STATUS = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('FLAGGED', 'Flagged'),
        ('REJECTED', 'Rejected'),
        ('LOCKED', 'Locked for Audit'),
    ]

    # Tenancy & source tracking
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    source_row_id = models.CharField(max_length=255)

    # Scope & category
    scope = models.IntegerField(choices=SCOPE_CHOICES)
    category = models.CharField(max_length=100)

    # Normalized activity data
    activity_value = models.DecimalField(max_digits=18, decimal_places=6)
    activity_unit = models.CharField(max_length=50)

    # Emissions
    emission_factor = models.DecimalField(
        max_digits=18, decimal_places=8, null=True, blank=True)
    emission_factor_source = models.CharField(
        max_length=255, null=True, blank=True)
    co2e_kg = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True)

    # Time period
    period_start = models.DateField()
    period_end = models.DateField()

    # Location
    facility_code = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)

    # Review
    review_status = models.CharField(
        max_length=20, choices=REVIEW_STATUS, default='PENDING')
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reviewed_records')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    # Flags
    has_warning = models.BooleanField(default=False)
    warning_reason = models.TextField(blank=True)

    # Audit trail
    raw_data = models.JSONField()
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} | {self.period_start} | {self.co2e_kg} kgCO2e"


class AuditLog(models.Model):
    record = models.ForeignKey(
        EmissionRecord, on_delete=models.CASCADE, related_name='audit_logs')
    actor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on record {self.record_id} at {self.timestamp}"