"""
User and authentication models with tenant isolation.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.managers.usermanager import UserManager
from core.models import TimeStampedModel


class UserRole(models.TextChoices):
    """User roles within a tenant."""
    TENANT_ADMIN = 'tenant_admin', _('Tenant Admin')
    TENANT_USER = 'tenant_user', _('Tenant User')
    ADMIN = 'admin', _('Admin')


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom User model with tenant association and address information.
    Each user belongs to exactly one tenant.
    """
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        help_text=_("Tenant this user belongs to")
    )

    # Authentication fields
    email = models.EmailField(
        unique=True,
        help_text=_("User's email address (used for login)")
    )

    # Personal information
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # Address information (required)
    address_line1 = models.CharField(
        max_length=255,
        help_text=_("Street address line 1")
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Street address line 2 (optional)")
    )
    city = models.CharField(
        max_length=100,
        help_text=_("City")
    )
    state = models.CharField(
        max_length=100,
        help_text=_("State/Province")
    )
    country = models.CharField(
        max_length=100,
        help_text=_("Country")
    )
    postal_code = models.CharField(
        max_length=20,
        help_text=_("Postal/ZIP code")
    )

    # Role within tenant
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.TENANT_USER,
        help_text=_("User's role within their tenant")
    )

    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this user should be treated as active.")
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user can log into admin site.")
    )

    # Metadata
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tenant', 'role']),
            models.Index(fields=['tenant', 'is_active']),
        ]
        constraints = [
            # Superusers can exist without tenant, but regular users must have one
            models.CheckConstraint(
                check=models.Q(is_superuser=True) | models.Q(tenant__isnull=False),
                name='regular_users_must_have_tenant'
            )
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email

    @property
    def is_tenant_admin(self):
        """Check if user has tenant admin role."""
        return self.role == UserRole.TENANT_ADMIN

    @property
    def full_address(self):
        """Return formatted full address."""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, parts))
