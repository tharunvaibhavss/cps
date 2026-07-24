from django.db import models
import uuid
from apps.bookings.models import PickupRequest

class TrackingLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(PickupRequest, on_delete=models.CASCADE, related_name='tracking_logs')
    status = models.CharField(max_length=50)
    location_name = models.CharField(max_length=150)
    latitude = models.FloatField(default=13.0827)
    longitude = models.FloatField(default=80.2707)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.tracking_number} -> {self.status} at {self.timestamp}"
