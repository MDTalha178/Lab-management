"""
Serializers for User authentication and management.
"""
from django.contrib.auth import authenticate
from rest_framework import serializers

from core.middleware import get_current_tenant
from .models import User, UserRole


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'tenant', 'tenant_name',
            'address_line1', 'address_line2', 'city', 'state',
            'country', 'postal_code',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user within a tenant."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name',
            'phone_number', 'role',
            'address_line1', 'address_line2', 'city', 'state',
            'country', 'postal_code'
        ]

    def validate_role(self, value):
        """Ensure role is valid."""
        if value not in [UserRole.TENANT_ADMIN, UserRole.TENANT_USER]:
            raise serializers.ValidationError("Invalid role specified.")
        return value

    def create(self, validated_data):
        """Create user and associate with current tenant."""

        tenant = get_current_tenant()
        if not tenant:
            raise serializers.ValidationError(
                "Cannot create user without tenant context."
            )

        password = validated_data.pop('password')
        user = User.objects.create_user(
            tenant=tenant,
            password=password,
            **validated_data
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number',
            'address_line1', 'address_line2', 'city', 'state',
            'country', 'postal_code'
        ]


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Validate credentials."""
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = User.objects.filter(
                email=email
            ).first()

            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.'
                )

            if user.check_password(password) is False:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.'
                )

            if user.role != 'admin' and (not user.tenant or not user.tenant.is_active):
                raise serializers.ValidationError(
                    'Your organization account is inactive.'
                )

        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".'
            )

        attrs['user'] = user
        return attrs
