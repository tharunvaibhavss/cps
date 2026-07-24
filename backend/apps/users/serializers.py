from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SavedAddress

User = get_user_model()

class SavedAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedAddress
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

class UserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_verified', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')
