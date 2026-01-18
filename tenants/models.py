"""
Tenant models for multi-tenant architecture.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel


class Tenant(TimeStampedModel):
    """
    Represents an organization/lab in the system.
    Each tenant has complete data isolation.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Unique name of the tenant/organization")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text=_("URL-friendly identifier for the tenant")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this tenant is currently active")
    )

    # Contact Information
    contact_email = models.EmailField(
        blank=True,
        null=True,
        help_text=_("Primary contact email for the tenant")
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Primary contact phone number")
    )

    # Address Information
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    # Metadata
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Tenant-specific configuration settings")
    )

    class Meta:
        db_table = 'tenants'
        ordering = ['-created_at']
        verbose_name = _("Tenant")
        verbose_name_plural = _("Tenants")
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def deactivate(self):
        """Deactivate this tenant and all associated users."""
        self.is_active = False
        self.save(update_fields=['is_active'])
        self.users.update(is_active=False)

    def activate(self):
        """Activate this tenant."""
        self.is_active = True
        self.save(update_fields=['is_active'])