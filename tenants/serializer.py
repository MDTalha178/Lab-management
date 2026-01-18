from django.utils.text import slugify
from rest_framework import serializers

from tenants.models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    """
    Serializer for Tenant model.
    """

    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'is_active',
            'contact_email', 'contact_phone',
            'address_line1', 'address_line2', 'city',
            'state', 'country', 'postal_code',
            'settings', 'user_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'user_count']

    @staticmethod
    def get_user_count(obj):
        """
        Get count of active users in tenant.
        """
        return obj.users.filter(is_active=True).count()

    def create(self, validated_data):
        """
        Create tenant with auto-generated slug.
        """
        if 'slug' not in validated_data or not validated_data['slug']:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


# Create your views here.
class TenantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new tenant with admin user."""

    # Admin user details
    admin_email = serializers.EmailField(write_only=True)
    admin_password = serializers.CharField(write_only=True, min_length=8)
    admin_first_name = serializers.CharField(write_only=True)
    admin_last_name = serializers.CharField(write_only=True)
    admin_phone = serializers.CharField(write_only=True, required=False)
    admin_address_line1 = serializers.CharField(write_only=True)
    admin_address_line2 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    admin_city = serializers.CharField(write_only=True)
    admin_state = serializers.CharField(write_only=True)
    admin_country = serializers.CharField(write_only=True)
    admin_postal_code = serializers.CharField(write_only=True)

    class Meta:
        model = Tenant
        fields = [
            'name', 'contact_email', 'contact_phone',
            'address_line1', 'address_line2', 'city',
            'state', 'country', 'postal_code',
            'admin_email', 'admin_password', 'admin_first_name', 'admin_last_name',
            'admin_phone', 'admin_address_line1', 'admin_address_line2',
            'admin_city', 'admin_state', 'admin_country', 'admin_postal_code'
        ]

    def create(self, validated_data):
        """Create tenant and admin user together."""
        from accounts.models import User, UserRole
        from django.db import transaction

        # Extract admin user data
        admin_data = {
            'email': validated_data.pop('admin_email'),
            'password': validated_data.pop('admin_password'),
            'first_name': validated_data.pop('admin_first_name'),
            'last_name': validated_data.pop('admin_last_name'),
            'phone_number': validated_data.pop('admin_phone', ''),
            'address_line1': validated_data.pop('admin_address_line1'),
            'address_line2': validated_data.pop('admin_address_line2', ''),
            'city': validated_data.pop('admin_city'),
            'state': validated_data.pop('admin_state'),
            'country': validated_data.pop('admin_country'),
            'postal_code': validated_data.pop('admin_postal_code'),
        }

        with transaction.atomic():
            # Create tenant
            validated_data['slug'] = slugify(validated_data['name'])
            tenant = Tenant.objects.create(**validated_data)

            # Create admin user
            admin_user = User.objects.create_user(
                tenant=tenant,
                role=UserRole.TENANT_ADMIN,
                **admin_data
            )

        return tenant