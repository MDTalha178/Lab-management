"""
Domain models for Patient, Test, and Sample management.
All models are tenant-scoped for complete data isolation.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from core.models import TenantAwareModel


class Patient(TenantAwareModel):
    """
    Represents a patient in the lab system.
    Each patient belongs to a specific tenant and can have multiple tests.
    """
    # Unique identifier within tenant
    patient_id = models.CharField(
        max_length=50,
        help_text=_("Unique patient identifier within the tenant")
    )

    # Personal Information
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ]
    )

    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)

    # Address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    # Medical Information
    blood_group = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ]
    )
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")
        indexes = [
            models.Index(fields=['tenant', 'patient_id']),
            models.Index(fields=['tenant', 'last_name', 'first_name']),
            models.Index(fields=['tenant', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'patient_id'],
                name='unique_patient_id_per_tenant'
            )
        ]

    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """Calculate patient's age."""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class TestType(TenantAwareModel):
    """
    Defines types of tests that can be performed.
    Each tenant can define their own test types.
    """
    code = models.CharField(
        max_length=50,
        help_text=_("Unique test type code within tenant")
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Test specifications
    category = models.CharField(
        max_length=100,
        help_text=_("Category of test (e.g., Blood Test, Urine Test, etc.)")
    )
    normal_range = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Normal range for test results")
    )
    unit_of_measurement = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Unit of measurement (e.g., mg/dL, mmol/L)")
    )

    # Pricing and timing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Cost of the test")
    )
    estimated_duration_hours = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("Estimated time to complete test in hours")
    )

    # Sample requirements
    requires_sample = models.BooleanField(
        default=True,
        help_text=_("Whether this test requires a physical sample")
    )
    sample_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Type of sample required (e.g., Blood, Urine, Tissue)")
    )
    sample_volume_ml = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Required sample volume in milliliters")
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'test_types'
        ordering = ['category', 'name']
        verbose_name = _("Test Type")
        verbose_name_plural = _("Test Types")
        indexes = [
            models.Index(fields=['tenant', 'code']),
            models.Index(fields=['tenant', 'category']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='unique_test_type_code_per_tenant'
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Test(TenantAwareModel):
    """
    Represents a test ordered for a patient.
    Links patient to test type and manages test lifecycle.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SAMPLE_COLLECTED = 'sample_collected', _('Sample Collected')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')

    test_number = models.CharField(
        max_length=50,
        help_text=_("Unique test number within tenant")
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name='tests'
    )
    test_type = models.ForeignKey(
        TestType,
        on_delete=models.PROTECT,
        related_name='tests'
    )

    # Test details
    ordered_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='ordered_tests',
        help_text=_("User who ordered this test")
    )
    ordered_at = models.DateTimeField(auto_now_add=True)

    # Status and scheduling
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('routine', 'Routine'),
            ('urgent', 'Urgent'),
            ('stat', 'STAT'),
        ],
        default='routine'
    )
    scheduled_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Scheduled date for test")
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Date and time when test was completed")
    )

    # Clinical information
    clinical_notes = models.TextField(
        blank=True,
        null=True,
        help_text=_("Clinical notes or reason for test")
    )

    # Results
    result_value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Test result value")
    )
    result_interpretation = models.TextField(
        blank=True,
        null=True,
        help_text=_("Interpretation of results")
    )
    is_abnormal = models.BooleanField(
        default=False,
        help_text=_("Flag for abnormal results")
    )
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='reviewed_tests',
        blank=True,
        null=True,
        help_text=_("User who reviewed the results")
    )
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Date and time of review")
    )

    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tests'
        ordering = ['-ordered_at']
        verbose_name = _("Test")
        verbose_name_plural = _("Tests")
        indexes = [
            models.Index(fields=['tenant', 'test_number']),
            models.Index(fields=['tenant', 'patient', 'status']),
            models.Index(fields=['tenant', 'status', 'ordered_at']),
            models.Index(fields=['tenant', 'test_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'test_number'],
                name='unique_test_number_per_tenant'
            )
        ]

    def __str__(self):
        return f"{self.test_number} - {self.patient.full_name} - {self.test_type.name}"


class Sample(TenantAwareModel):
    """
    Represents a physical sample collected for testing.
    Tracks collection, storage, and processing status.
    """

    class Status(models.TextChoices):
        COLLECTED = 'collected', _('Collected')
        IN_TRANSIT = 'in_transit', _('In Transit')
        RECEIVED = 'received', _('Received')
        PROCESSING = 'processing', _('Processing')
        PROCESSED = 'processed', _('Processed')
        REJECTED = 'rejected', _('Rejected')
        DISCARDED = 'discarded', _('Discarded')

    sample_id = models.CharField(
        max_length=50,
        help_text=_("Unique sample identifier within tenant")
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.PROTECT,
        related_name='samples'
    )

    # Sample details
    sample_type = models.CharField(
        max_length=100,
        help_text=_("Type of sample (Blood, Urine, Tissue, etc.)")
    )
    volume_ml = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Sample volume in milliliters")
    )

    # Collection information
    collected_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='collected_samples'
    )
    collected_at = models.DateTimeField()
    collection_method = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Method used for collection")
    )
    collection_site = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Anatomical site of collection")
    )

    # Storage and handling
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COLLECTED
    )
    storage_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Current storage location")
    )
    storage_temperature = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Required storage temperature")
    )

    # Processing
    processed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='processed_samples',
        blank=True,
        null=True
    )
    processed_at = models.DateTimeField(blank=True, null=True)

    # Quality control
    quality_acceptable = models.BooleanField(
        default=True,
        help_text=_("Whether sample quality is acceptable for testing")
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text=_("Reason for sample rejection")
    )

    # Contamination and special handling
    is_hazardous = models.BooleanField(
        default=False,
        help_text=_("Flag for hazardous samples")
    )
    special_handling_instructions = models.TextField(
        blank=True,
        null=True
    )

    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'samples'
        ordering = ['-collected_at']
        verbose_name = _("Sample")
        verbose_name_plural = _("Samples")
        indexes = [
            models.Index(fields=['tenant', 'sample_id']),
            models.Index(fields=['tenant', 'test', 'status']),
            models.Index(fields=['tenant', 'status', 'collected_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'sample_id'],
                name='unique_sample_id_per_tenant'
            )
        ]

    def __str__(self):
        return f"{self.sample_id} - {self.sample_type} for {self.test.test_number}"


from django.db import models

# Create your models here.
