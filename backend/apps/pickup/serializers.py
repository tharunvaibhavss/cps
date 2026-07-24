from rest_framework import serializers
from .models import ProofOfPickup
from apps.bookings.serializers import PickupRequestSerializer

class ProofOfPickupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProofOfPickup
        fields = '__all__'
        read_only_fields = ('id', 'verified_at')
