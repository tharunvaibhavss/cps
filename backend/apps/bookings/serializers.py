from rest_framework import serializers
from .models import PickupRequest, PickupSlot, BookingTemplate, HolidayCalendar, ServiceArea
from apps.authentication.serializers import UserSerializer

class PickupSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupSlot
        fields = '__all__'

class PickupRequestSerializer(serializers.ModelSerializer):
    customer_detail = UserSerializer(source='customer', read_only=True)
    agent_detail = UserSerializer(source='agent', read_only=True)

    class Meta:
        model = PickupRequest
        fields = '__all__'
        read_only_fields = ('id', 'tracking_number', 'customer', 'status', 'qr_code_str', 'created_at', 'updated_at')

    def create(self, validated_data):
        request = self.context['request']
        validated_data['customer'] = request.user
        return super().create(validated_data)

class BookingTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingTemplate
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class HolidayCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayCalendar
        fields = '__all__'

class ServiceAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceArea
        fields = '__all__'
