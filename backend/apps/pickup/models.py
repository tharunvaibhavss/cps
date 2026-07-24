from django.db import models
from django.conf import settings
import uuid
from apps.bookings.models import PickupRequest

class ProofOfPickup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(PickupRequest, on_delete=models.CASCADE, related_name='proof')
    signature_data_url = models.TextField(help_text="Base64 Canvas Signature string")
    photo = models.ImageField(upload_to='proofs/', blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    voice_note_text = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proof for {self.booking.tracking_number} at {self.verified_at}"
