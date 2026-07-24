from django.urls import path
from .views import LiveTrackingView, UpdateLocationView

urlpatterns = [
    path('update-location/', UpdateLocationView.as_view(), name='update-location'),
    path('<str:tracking_number>/', LiveTrackingView.as_view(), name='live-tracking'),
]
