"""
Middleware for tenant resolution and enforcement.
Ensures all requests operate within the correct tenant context.
"""
import threading
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework import status

from core.auth import AuthenticationService

# Thread-local storage for tenant context
_thread_locals = threading.local()


def get_current_tenant():
    """
    Get the current tenant from thread-local storage.
    """
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    """
    Set the current tenant in thread-local storage.
    """
    _thread_locals.tenant = tenant


def clear_current_tenant():
    """
    Clear the current tenant from thread-local storage.
    """
    if hasattr(_thread_locals, 'tenant'):
        delattr(_thread_locals, 'tenant')


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to resolve and set tenant context for each request.

    Tenant is resolved from the authenticated user's tenant association.
    This ensures complete tenant isolation at the middleware level.
    """

    EXCLUDED_PATHS = [
        '/admin/',
        '/api/v1/auth/register/',
        '/api/v1/auth/login/',
        '/api/v1/auth/refresh/',
        '/api/v1/tenants/register/',
        '/api/v1/tenants/create-tenant/',
        '/swagger/',
        '/redoc/',
        '/api/schema/',
    ]

    def process_request(self, request):
        """
        Process incoming request and set tenant context.
        """
        # Clear any existing tenant context
        clear_current_tenant()

        print(request.path)

        # Skip tenant resolution for excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return None

        user, token = AuthenticationService().authenticate(request)

        # Skip for unauthenticated requests (will be handled by auth)
        # if not request.user or not request.user.is_authenticated:
        #     return None

        if user is None:
            return JsonResponse(
                {
                    'error': 'Credential Missing',
                    'detail': 'unable to authenticate your account'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Get tenant from authenticated user
        if not hasattr(user, 'tenant') or not user.tenant:
            return JsonResponse(
                {
                    'error': 'No tenant associated with user',
                    'detail': 'Your account is not associated with any organization.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        tenant = user.tenant

        # Check if tenant is active
        if not tenant.is_active:
            return JsonResponse(
                {
                    'error': 'Tenant inactive',
                    'detail': 'Your organization account has been deactivated.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Set tenant in thread-local storage
        set_current_tenant(tenant)

        # Also attach to request for easy access
        request.tenant = tenant

        return None

    def process_response(self, request, response):
        """
        Clean up tenant context after request processing.
        """
        clear_current_tenant()
        return response

    def process_exception(self, request, exception):
        """
        Clean up tenant context if an exception occurs.
        """
        clear_current_tenant()
        return None