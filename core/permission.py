"""
Custom permissions for role-based access control.
"""
from rest_framework import permissions

from accounts.models import UserRole


class IsTenantAdmin(permissions.BasePermission):
    """
    Permission to check if user is a tenant admin.
    """
    message = "Only tenant administrators can perform this action."

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.role == UserRole.TENANT_ADMIN
        )


class IsTenantUser(permissions.BasePermission):
    """
    Permission to check if user is a tenant user (any role within tenant).
    """
    message = "You must be a member of a tenant to perform this action."

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                hasattr(request.user, 'tenant') and
                request.user.tenant is not None
        )


class IsTenantAdminOrReadOnly(permissions.BasePermission):
    """
    Tenant admins have full access, others have read-only.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role == UserRole.TENANT_ADMIN


class IsSameTenant(permissions.BasePermission):
    """
    Object-level permission to only allow access to objects within same tenant.
    """
    message = "You can only access resources within your organization."

    def has_object_permission(self, request, view, obj):
        # Superusers can access everything

        # Check if object has tenant attribute
        if not hasattr(obj, 'tenant'):
            return False

        # Check if user's tenant matches object's tenant
        return (
                hasattr(request.user, 'tenant') and
                request.user.tenant == obj.tenant
        )