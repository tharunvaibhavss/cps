from rest_framework import serializers, views, permissions, status
from django.shortcuts import get_object_or_404
from .models import TrackingLog
from apps.bookings.models import PickupRequest, PickupStatusChoices

class TrackingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingLog
        fields = '__all__'

class LiveTrackingView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, tracking_number):
        booking = get_object_or_404(PickupRequest, tracking_number=tracking_number)
        logs = TrackingLog.objects.filter(booking=booking).order_by('timestamp')

        # Standard timeline steps definition
        timeline_steps = [
            {'key': 'PENDING', 'label': 'Booking Created', 'completed': True},
            {'key': 'ASSIGNED', 'label': 'Agent Assigned', 'completed': booking.status in ['ASSIGNED', 'ON_THE_WAY', 'PICKED', 'SORTING', 'TRANSIT', 'DELIVERED']},
            {'key': 'ON_THE_WAY', 'label': 'Agent On The Way', 'completed': booking.status in ['ON_THE_WAY', 'PICKED', 'SORTING', 'TRANSIT', 'DELIVERED']},
            {'key': 'PICKED', 'label': 'Package Picked', 'completed': booking.status in ['PICKED', 'SORTING', 'TRANSIT', 'DELIVERED']},
            {'key': 'TRANSIT', 'label': 'In Transit', 'completed': booking.status in ['SORTING', 'TRANSIT', 'DELIVERED']},
            {'key': 'DELIVERED', 'label': 'Delivered', 'completed': booking.status == 'DELIVERED'},
        ]

        # Simulating live agent position relative to pickup location
        current_agent_lat = booking.pickup_lat + 0.005
        current_agent_lng = booking.pickup_lng + 0.005

        delay_prediction = {
            'is_delayed': False,
            'predicted_delay_mins': 0,
            'reason': 'Clear roads & smooth weather conditions',
            'confidence': '94%'
        }

        return Response({
            'booking_id': str(booking.id),
            'tracking_number': booking.tracking_number,
            'status': booking.status,
            'customer_name': booking.pickup_contact_name,
            'pickup_address': booking.pickup_address,
            'pickup_lat': booking.pickup_lat,
            'pickup_lng': booking.pickup_lng,
            'delivery_address': booking.delivery_address,
            'delivery_lat': booking.delivery_lat,
            'delivery_lng': booking.delivery_lng,
            'agent_name': booking.agent.get_full_name() if booking.agent else "Assigning Courier Agent",
            'agent_phone': booking.agent.phone if booking.agent else "+1 (800) 555-0199",
            'current_agent_location': {
                'lat': current_agent_lat,
                'lng': current_agent_lng,
                'last_updated': 'Just now'
            },
            'eta_mins': 18,
            'timeline': timeline_steps,
            'delay_prediction': delay_prediction,
            'logs': TrackingLogSerializer(logs, many=True).data
        })

class UpdateLocationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        tracking_number = request.data.get('tracking_number')
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        status_name = request.data.get('status', 'ON_THE_WAY')
        location_name = request.data.get('location_name', 'En Route')

        booking = get_object_or_404(PickupRequest, tracking_number=tracking_number)
        log = TrackingLog.objects.create(
            booking=booking,
            status=status_name,
            location_name=location_name,
            latitude=lat,
            longitude=lng,
            description=f"GPS coordinate update received: ({lat}, {lng})"
        )
        return Response({'message': 'Location updated successfully', 'log': TrackingLogSerializer(log).data})
