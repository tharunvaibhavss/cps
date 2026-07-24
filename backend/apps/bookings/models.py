from django.db import models
from django.conf import settings
import uuid

class PickupStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending Agent Assignment'
    ASSIGNED = 'ASSIGNED', 'Agent Assigned'
    ON_THE_WAY = 'ON_THE_WAY', 'Agent On The Way'
    PICKED = 'PICKED', 'Package Picked Up'
    SORTING = 'SORTING', 'Sorting Center'
    TRANSIT = 'TRANSIT', 'In Transit'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'

class PackageCategoryChoices(models.TextChoices):
    DOCUMENTS = 'DOCUMENTS', 'Documents & Letters'
    ELECTRONICS = 'ELECTRONICS', 'Electronics & Gadgets'
    CLOTHING = 'CLOTHING', 'Clothing & Apparel'
    FRAGILE = 'FRAGILE', 'Fragile & Glassware'
    FOOD_PERISHABLE = 'FOOD_PERISHABLE', 'Food & Perishables'
    HEAVY_CARGO = 'HEAVY_CARGO', 'Heavy / Large Cargo'
    OTHER = 'OTHER', 'Other Merchandise'

class PickupSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    slot_time = models.CharField(max_length=50, help_text="e.g. 09:00 AM - 12:00 PM")
    max_capacity = models.PositiveIntegerField(default=20)
    current_bookings = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def is_available(self):
        return self.is_active and self.current_bookings < self.max_capacity

    def __str__(self):
        return f"{self.date} [{self.slot_time}] ({self.current_bookings}/{self.max_capacity})"

class PickupRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracking_number = models.CharField(max_length=30, unique=True, db_index=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', db_index=True)
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_pickups', db_index=True)
    
    status = models.CharField(max_length=30, choices=PickupStatusChoices.choices, default=PickupStatusChoices.PENDING, db_index=True)
    
    # Pickup details
    pickup_contact_name = models.CharField(max_length=100)
    pickup_phone = models.CharField(max_length=20)
    pickup_address = models.TextField()
    pickup_lat = models.FloatField(default=13.0827)
    pickup_lng = models.FloatField(default=80.2707)
    
    # Delivery details
    delivery_contact_name = models.CharField(max_length=100)
    delivery_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    delivery_lat = models.FloatField(default=13.0900)
    delivery_lng = models.FloatField(default=80.2800)

    # Package Specs
    package_name = models.CharField(max_length=150)
    package_category = models.CharField(max_length=30, choices=PackageCategoryChoices.choices, default=PackageCategoryChoices.DOCUMENTS)
    package_image = models.ImageField(upload_to='packages/', blank=True, null=True)
    approx_weight_kg = models.FloatField(default=1.0)
    package_size = models.CharField(max_length=50, default='Small (0.5m x 0.5m)')
    is_fragile = models.BooleanField(default=False)
    special_instructions = models.TextField(blank=True, null=True)
    
    # Slot & Timing
    pickup_date = models.DateField(db_index=True)
    pickup_slot_time = models.CharField(max_length=50, default='09:00 AM - 12:00 PM')
    
    # Billing & QR
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, default=150.00)
    qr_code_str = models.CharField(max_length=100, blank=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"CPS-{uuid.uuid4().hex[:8].upper()}"
        if not self.qr_code_str:
            self.qr_code_str = f"QR-{self.tracking_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_number} - {self.status}"

class BookingTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='templates')
    template_name = models.CharField(max_length=100, help_text="e.g. Office to Warehouse Daily")
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    package_category = models.CharField(max_length=30, choices=PackageCategoryChoices.choices, default=PackageCategoryChoices.DOCUMENTS)
    created_at = models.DateTimeField(auto_now_add=True)

class HolidayCalendar(models.Model):
    date = models.DateField(unique=True)
    title = models.CharField(max_length=100)
    is_operational = models.BooleanField(default=False)

class ServiceArea(models.Model):
    name = models.CharField(max_length=100)
    postal_code_prefix = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
