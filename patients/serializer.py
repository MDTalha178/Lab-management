from rest_framework import serializers

from core.utils import get_current_tenant
from patients.models import Patient, Sample, Test, TestType


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model."""

    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    test_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'gender', 'email', 'phone_number',
            'address_line1', 'address_line2', 'city', 'state',
            'country', 'postal_code',
            'blood_group', 'medical_history', 'allergies', 'current_medications',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship',
            'is_active', 'notes', 'test_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']

    def create(self, validated_data):
        try:
            print("We are here")
            patient = Patient.objects.create(
                tenant=get_current_tenant(),
                **validated_data

            )
            return patient
        except Exception as e:
            print(e)
            raise serializers.ValidationError("Something went wrong")

    def get_test_count(self, obj):
        """Get count of tests for this patient."""
        return obj.tests.count()


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for patient lists."""

    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'full_name', 'age', 'gender',
            'phone_number', 'city', 'is_active'
        ]


class TestTypeSerializer(serializers.ModelSerializer):
    """Serializer for TestType model."""

    class Meta:
        model = TestType
        fields = [
            'id', 'code', 'name', 'description', 'category',
            'normal_range', 'unit_of_measurement', 'price',
            'estimated_duration_hours', 'requires_sample',
            'sample_type', 'sample_volume_ml', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']


class TestSerializer(serializers.ModelSerializer):
    """Serializer for Test model."""

    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    test_type_name = serializers.CharField(source='test_type.name', read_only=True)
    ordered_by_name = serializers.CharField(source='ordered_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    sample_count = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = [
            'id', 'test_number', 'patient', 'patient_name',
            'test_type', 'test_type_name', 'ordered_by', 'ordered_by_name',
            'ordered_at', 'status', 'priority', 'scheduled_date',
            'completed_at', 'clinical_notes', 'result_value',
            'result_interpretation', 'is_abnormal', 'reviewed_by',
            'reviewed_by_name', 'reviewed_at', 'notes', 'sample_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'tenant', 'test_number', 'ordered_by', 'ordered_at',
            'created_at', 'updated_at', 'reviewed_by'
        ]

    def get_sample_count(self, obj):
        """Get count of samples for this test."""
        return obj.samples.count()

    def create(self, validated_data):
        """
        Create test with auto-generated test number.
        """
        import uuid

        tenant = get_current_tenant()
        validated_data['tenant'] = tenant
        validated_data['ordered_by_id'] = self.context['user_id']
        validated_data['reviewed_by_id'] = self.context['user_id']

        # Generate unique test number
        validated_data['test_number'] = f"T-{uuid.uuid4().hex[:8].upper()}"

        return super().create(validated_data)


class TestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for test lists."""

    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    test_type_name = serializers.CharField(source='test_type.name', read_only=True)

    class Meta:
        model = Test
        fields = [
            'id', 'test_number', 'patient_name', 'test_type_name',
            'status', 'priority', 'ordered_at', 'is_abnormal'
        ]


class SampleSerializer(serializers.ModelSerializer):
    """Serializer for Sample model."""

    test_number = serializers.CharField(source='test.test_number', read_only=True)
    patient_name = serializers.CharField(source='test.patient.full_name', read_only=True)
    collected_by_name = serializers.CharField(
        source='collected_by.get_full_name',
        read_only=True
    )
    processed_by_name = serializers.CharField(
        source='processed_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Sample
        fields = [
            'id', 'sample_id', 'test', 'test_number', 'patient_name',
            'sample_type', 'volume_ml', 'collected_by', 'collected_by_name',
            'collected_at', 'collection_method', 'collection_site',
            'status', 'storage_location', 'storage_temperature',
            'processed_by', 'processed_by_name', 'processed_at',
            'quality_acceptable', 'rejection_reason', 'is_hazardous',
            'special_handling_instructions', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'tenant', 'sample_id', 'collected_by',
            'created_at', 'updated_at', 'processed_by'
        ]

    def create(self, validated_data):
        """Create sample with auto-generated sample ID."""
        import uuid

        tenant = get_current_tenant()
        validated_data['tenant'] = tenant
        validated_data['collected_by_id'] = self.context['user_id']
        validated_data['processed_by_id'] = self.context['user_id']

        # Generate unique sample ID
        validated_data['sample_id'] = f"S-{uuid.uuid4().hex[:8].upper()}"

        return super().create(validated_data)


class SampleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for sample lists."""

    test_number = serializers.CharField(source='test.test_number', read_only=True)
    patient_name = serializers.CharField(source='test.patient.full_name', read_only=True)

    class Meta:
        model = Sample
        fields = [
            'id', 'sample_id', 'test_number', 'patient_name',
            'sample_type', 'status', 'collected_at', 'quality_acceptable'
        ]