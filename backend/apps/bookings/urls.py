from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookingViewSet, AIPackageDetectionView, VoiceBookingParseView,
    SlotRecommendationView, PickupSlotViewSet, BookingTemplateViewSet,
    HolidayViewSet, ServiceAreaViewSet
)

router = DefaultRouter()
router.register(r'requests', BookingViewSet, basename='booking-request')
router.register(r'slots', PickupSlotViewSet, basename='pickup-slot')
router.register(r'templates', BookingTemplateViewSet, basename='booking-template')
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'service-areas', ServiceAreaViewSet, basename='service-area')

urlpatterns = [
    path('ai-detect-package/', AIPackageDetectionView.as_view(), name='ai-detect-package'),
    path('parse-voice/', VoiceBookingParseView.as_view(), name='parse-voice'),
    path('recommend-slots/', SlotRecommendationView.as_view(), name='recommend-slots'),
    path('', include(router.urls)),
]
