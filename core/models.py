"""
Core abstract models for the application.
Provides common functionality for all models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import get_current_tenant


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides timestamp fields.
    All models should inherit from this or TenantAwareModel.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when the record was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp when the record was last updated")
    )

    class Meta:
        abstract = True


class TenantAwareModel(TimeStampedModel):
    """
    Abstract base model for tenant-scoped data.
    Ensures all data is associated with a tenant for proper isolation.
    """
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        help_text=_("Tenant that owns this record")
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Override save to ensure tenant is set.
        Tenant should be set by middleware or explicitly.
        """
        if not self.tenant_id:
            tenant = get_current_tenant()
            if tenant:
                self.tenant = tenant
            else:
                raise ValueError(
                    "Cannot save tenant-aware model without tenant context. "
                    "Please ensure tenant middleware is active or set tenant explicitly."
                )
        super().save(*args, **kwargs)