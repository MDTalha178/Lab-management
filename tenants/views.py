from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny

from core.utils import CustomModelView
from tenants.models import Tenant
from tenants.serializer import TenantSerializer, TenantCreateSerializer


class TenantViewSet(CustomModelView):
    """
    ViewSet for Tenant management.
    Only superusers can manage tenants.
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAdminUser]

    http_method_names = ('post', )

    def get_serializer_class(self):
        """
        Use different serializer for creation.
        """
        if self.action == 'create' or self.action == 'register':
            return TenantCreateSerializer
        return TenantSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Public endpoint for tenant registration.
        Creates both tenant and initial admin user.
        """
        serializer = TenantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = serializer.save()

        return self.success_response(
            message='Tenant registered successfully',
            data=TenantSerializer(tenant).data,
            status_code=status.HTTP_201_CREATED
        )