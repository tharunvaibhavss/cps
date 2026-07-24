from django.db import models
from django.conf import settings
import uuid

class AddressTagChoices(models.TextChoices):
    HOME = 'HOME', 'Home'
    OFFICE = 'OFFICE', 'Office'
    WAREHOUSE = 'WAREHOUSE', 'Warehouse'
    CUSTOM = 'CUSTOM', 'Custom'

class SavedAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=100, help_text="e.g. My Apartment, Main Warehouse")
    tag = models.CharField(max_length=20, choices=AddressTagChoices.choices, default=AddressTagChoices.HOME)
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    landmark = models.CharField(max_length=150, blank=True, null=True)
    latitude = models.FloatField(default=13.0827) # Default Chennai/City center coords
    longitude = models.FloatField(default=80.2707)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            SavedAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.tag}) - {self.city}"
