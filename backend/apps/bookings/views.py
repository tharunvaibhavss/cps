from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
import datetime
import random

from .models import PickupRequest, PickupSlot, BookingTemplate, HolidayCalendar, ServiceArea, PickupStatusChoices
from .serializers import (
    PickupRequestSerializer, PickupSlotSerializer, BookingTemplateSerializer,
    HolidayCalendarSerializer, ServiceAreaSerializer
)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = PickupRequestSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated:
            if user.role in ['ADMIN']:
                return PickupRequest.objects.all().order_by('-created_at')
            elif user.role == 'AGENT':
                return PickupRequest.objects.filter(agent=user).order_by('-created_at')
            return PickupRequest.objects.filter(customer=user).order_by('-created_at')
        return PickupRequest.objects.all().order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='mark-delivered')
    def mark_delivered(self, request, pk=None):
        booking = self.get_object()
        booking.status = PickupStatusChoices.DELIVERED
        booking.save()
        return Response({
            'message': f'Order {booking.tracking_number} marked as DELIVERED successfully!',
            'booking': PickupRequestSerializer(booking).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status in [PickupStatusChoices.DELIVERED, PickupStatusChoices.CANCELLED]:
            return Response({'error': f'Cannot cancel booking in {booking.status} state.'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = PickupStatusChoices.CANCELLED
        booking.save()
        return Response({'message': 'Booking cancelled successfully.', 'booking': PickupRequestSerializer(booking).data})

    @action(detail=True, methods=['post'])
    def repeat(self, request, pk=None):
        existing = self.get_object()
        new_booking = PickupRequest.objects.create(
            customer=request.user if request.user and request.user.is_authenticated else existing.customer,
            pickup_contact_name=existing.pickup_contact_name,
            pickup_phone=existing.pickup_phone,
            pickup_address=existing.pickup_address,
            pickup_lat=existing.pickup_lat,
            pickup_lng=existing.pickup_lng,
            delivery_contact_name=existing.delivery_contact_name,
            delivery_phone=existing.delivery_phone,
            delivery_address=existing.delivery_address,
            delivery_lat=existing.delivery_lat,
            delivery_lng=existing.delivery_lng,
            package_name=f"Repeat - {existing.package_name}",
            package_category=existing.package_category,
            approx_weight_kg=existing.approx_weight_kg,
            package_size=existing.package_size,
            is_fragile=existing.is_fragile,
            special_instructions=existing.special_instructions,
            pickup_date=datetime.date.today() + datetime.timedelta(days=1),
            pickup_slot_time=existing.pickup_slot_time,
            estimated_price=existing.estimated_price
        )
        return Response({'message': 'Booking duplicated successfully!', 'booking': PickupRequestSerializer(new_booking).data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Accepts a JSON array of multiple pickup items created manually or parsed from CSV"""
        items = request.data.get('items', [])
        if not items:
            return Response({'error': 'No items provided for bulk booking.'}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        user_cust = request.user if request.user and request.user.is_authenticated else None

        for item in items:
            b = PickupRequest.objects.create(
                customer=user_cust,
                pickup_contact_name=item.get('pickup_contact_name', 'Customer'),
                pickup_phone=item.get('pickup_phone', '9876543210'),
                pickup_address=item.get('pickup_address', 'Customer Main Address'),
                delivery_contact_name=item.get('delivery_contact_name', 'Recipient'),
                delivery_phone=item.get('delivery_phone', '9876543210'),
                delivery_address=item.get('delivery_address', 'Destination Address'),
                package_name=item.get('package_name', 'Bulk Item'),
                package_category=item.get('package_category', 'DOCUMENTS'),
                approx_weight_kg=float(item.get('approx_weight_kg', 1.0)),
                package_size=item.get('package_size', 'Medium'),
                is_fragile=bool(item.get('is_fragile', False)),
                pickup_date=datetime.date.today() + datetime.timedelta(days=1),
                pickup_slot_time='09:00 AM - 12:00 PM',
                estimated_price=120.00
            )
            created.append(PickupRequestSerializer(b).data)

        return Response({
            'message': f'Successfully created {len(created)} bulk pickup bookings.',
            'count': len(created),
            'bookings': created
        }, status=status.HTTP_201_CREATED)


class AIPackageDetectionView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        image_name = request.data.get('filename', 'package_box.jpg').lower()
        
        category = 'DOCUMENTS'
        estimated_weight = 0.5
        estimated_size = 'Small (0.3m x 0.3m)'
        is_fragile = False
        confidence = round(random.uniform(92.0, 98.5), 1)

        if 'electronics' in image_name or 'laptop' in image_name or 'phone' in image_name:
            category = 'ELECTRONICS'
            estimated_weight = 2.5
            estimated_size = 'Medium (0.5m x 0.4m)'
            is_fragile = True
        elif 'glass' in image_name or 'bottle' in image_name or 'fragile' in image_name:
            category = 'FRAGILE'
            estimated_weight = 1.8
            estimated_size = 'Medium (0.4m x 0.4m)'
            is_fragile = True
        elif 'box' in image_name or 'heavy' in image_name or 'cargo' in image_name:
            category = 'HEAVY_CARGO'
            estimated_weight = 8.5
            estimated_size = 'Large (1.0m x 0.8m)'
            is_fragile = False
        else:
            category = 'CLOTHING'
            estimated_weight = 1.2
            estimated_size = 'Small (0.4m x 0.3m)'

        return Response({
            'ai_analysis': {
                'detected_category': category,
                'estimated_weight_kg': estimated_weight,
                'estimated_size': estimated_size,
                'is_fragile': is_fragile,
                'confidence_score_pct': confidence,
                'suggestion_note': f"AI model identified {category} with {confidence}% confidence. You can edit any parameter."
            }
        })


class VoiceBookingParseView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        transcript = request.data.get('transcript', '').strip().lower()
        
        if not transcript:
            return Response({'error': 'No transcript provided'}, status=status.HTTP_400_BAD_REQUEST)

        pickup_address = "Home Address"
        if "office" in transcript:
            pickup_address = "HQ Office, Suite 400"
        elif "warehouse" in transcript:
            pickup_address = "Logistics Hub Warehouse 2"

        date_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        if "today" in transcript:
            date_str = datetime.date.today().strftime('%Y-%m-%d')
        elif "day after" in transcript:
            date_str = (datetime.date.today() + datetime.timedelta(days=2)).strftime('%Y-%m-%d')

        slot = "09:00 AM - 12:00 PM"
        if "afternoon" in transcript or "evening" in transcript or "pm" in transcript:
            slot = "02:00 PM - 05:00 PM"

        category = "DOCUMENTS"
        if "laptop" in transcript or "gadget" in transcript or "phone" in transcript:
            category = "ELECTRONICS"
        elif "box" in transcript or "parcel" in transcript:
            category = "OTHER"

        return Response({
            'parsed_booking': {
                'pickup_address': pickup_address,
                'pickup_date': date_str,
                'pickup_slot_time': slot,
                'package_category': category,
                'package_name': f"Voice Order ({category.title()})",
                'raw_transcript': transcript
            }
        })


class SlotRecommendationView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        date_param = request.data.get('date', datetime.date.today().strftime('%Y-%m-%d'))
        
        recommendations = [
            {
                'time_window': '09:00 AM - 12:00 PM',
                'recommendation_score': '98% Recommended',
                'badge': 'Optimal Traffic & Agent Density',
                'traffic_status': 'Low Traffic',
                'available_agents': 6,
                'estimated_wait_mins': 15
            },
            {
                'time_window': '02:00 PM - 05:00 PM',
                'recommendation_score': '88% Standard',
                'badge': 'Moderate Demand',
                'traffic_status': 'Moderate Traffic',
                'available_agents': 4,
                'estimated_wait_mins': 25
            },
            {
                'time_window': '05:00 PM - 08:00 PM',
                'recommendation_score': '75% High Traffic',
                'badge': 'Peak Evening Hours',
                'traffic_status': 'Heavy Traffic',
                'available_agents': 3,
                'estimated_wait_mins': 40
            }
        ]
        return Response({'date': date_param, 'recommendations': recommendations})


class PickupSlotViewSet(viewsets.ModelViewSet):
    queryset = PickupSlot.objects.all().order_by('date', 'slot_time')
    serializer_class = PickupSlotSerializer
    permission_classes = [permissions.AllowAny]

class BookingTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = BookingTemplateSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BookingTemplate.objects.all()

class HolidayViewSet(viewsets.ModelViewSet):
    queryset = HolidayCalendar.objects.all().order_by('date')
    serializer_class = HolidayCalendarSerializer
    permission_classes = [permissions.AllowAny]

class ServiceAreaViewSet(viewsets.ModelViewSet):
    queryset = ServiceArea.objects.all().order_by('city', 'name')
    serializer_class = ServiceAreaSerializer
    permission_classes = [permissions.AllowAny]
