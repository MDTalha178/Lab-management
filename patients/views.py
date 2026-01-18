from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action

from core.auth import AuthenticationService
from core.permission import IsTenantUser, IsSameTenant, IsTenantAdmin
from core.utils import CustomModelView
from patients.models import Patient, TestType, Test, Sample
from patients.serializer import PatientSerializer, PatientListSerializer, TestListSerializer, TestTypeSerializer, \
    TestSerializer, SampleSerializer, SampleListSerializer


# Create your views here.
class TenantFilteredViewSet(CustomModelView):
    """
    Base viewset with tenant filtering.
    """
    authentication_classes = [AuthenticationService, ]
    permission_classes = [IsTenantUser, IsSameTenant]

    def get_queryset(self):
        """
        Filter queryset to current tenant.
        """
        queryset = super().get_queryset()
        return queryset.filter(tenant=self.request.user.tenant)


class PatientViewSet(TenantFilteredViewSet):
    """
    ViewSet for Patient management.
    """
    http_method_names = ('post', 'get',)
    queryset = Patient.objects.select_related('tenant').all()
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'is_active', 'blood_group']
    search_fields = ['patient_id', 'first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['created_at', 'last_name', 'date_of_birth']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        Use lighter serializer for list view."""
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                patient = serializer.save()
                return self.success_response(
                    status_code=status.HTTP_201_CREATED, message="Patient Created",
                    data=PatientSerializer(patient).data
                )
            return self.failure_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors
            )
        except Exception as e:
            return self.failure_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Something went wrong"
            )

    # @action(detail=True, methods=['get'])
    # def tests(self, request, pk=None):
    #     """Get all tests for a specific patient."""
    #     patient = self.get_object()
    #     tests = patient.tests.select_related('test_type', 'ordered_by').all()
    #     serializer = TestListSerializer(tests, many=True)
    #     return self.success_response(data=serializer.data)


class TestTypeViewSet(TenantFilteredViewSet):
    """ViewSet for TestType management."""
    http_method_names = ('post', 'get',)
    queryset = TestType.objects.select_related('tenant').all()
    serializer_class = TestTypeSerializer
    authentication_classes = [AuthenticationService, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'requires_sample']
    search_fields = ['code', 'name', 'category']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['category', 'name']

    def get_permissions(self):
        """
        Only tenant admins can create/update/delete test types.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTenantAdmin(), IsSameTenant()]
        return [IsTenantUser(), IsSameTenant()]


class TestViewSet(TenantFilteredViewSet):
    """ViewSet for Test management."""
    http_method_names = ('get', 'post',)
    queryset = Test.objects.select_related(
        'tenant', 'patient', 'test_type', 'ordered_by', 'reviewed_by'
    ).all()
    serializer_class = TestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'is_abnormal', 'patient', 'test_type']
    search_fields = ['test_number', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['ordered_at', 'completed_at', 'status']
    ordering = ['-ordered_at']

    def get_serializer_class(self):
        """
        Use lighter serializer for list view.
        """
        if self.action == 'list':
            return TestListSerializer
        return TestSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data, context={'user_id': self.request.user_id})
            if serializer.is_valid(raise_exception=True):
                test = serializer.save()
                return self.success_response(
                    status_code=status.HTTP_201_CREATED,
                    message="Test created Successfully",
                    data=TestSerializer(test).data
                )
            return self.failure_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors
            )
        except Exception as e:
            print(e)
            return self.failure_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Something went wrong"
            )


class SampleViewSet(TenantFilteredViewSet):
    """ViewSet for Sample management."""

    queryset = Sample.objects.select_related(
        'tenant', 'test', 'test__patient', 'collected_by', 'processed_by'
    ).all()
    serializer_class = SampleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'sample_type', 'quality_acceptable', 'is_hazardous', 'test']
    search_fields = ['sample_id', 'test__test_number', 'test__patient__first_name']
    ordering_fields = ['collected_at', 'processed_at', 'status']
    ordering = ['-collected_at']

    def get_serializer_class(self):
        """Use lighter serializer for list view."""
        if self.action == 'list':
            return SampleListSerializer
        return SampleSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data, context={'user_id': self.request.user_id})
            if serializer.is_valid(raise_exception=True):
                sample = serializer.save()
                return self.success_response(
                    status_code=status.HTTP_201_CREATED,
                    message="Sample created Successfully",
                    data=SampleSerializer(sample).data
                )
            return self.failure_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors
            )
        except Exception as e:
            print(e)
            return self.failure_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Something went wrong"
            )
