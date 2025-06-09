from django.db import models
from django.db import models
from django.db import models

class FarmerProfile(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    gps = models.CharField(max_length=100, blank=True)
    farm_size = models.CharField(max_length=50, blank=True)

    crops = models.TextField(blank=True)  # comma separated
    planting_dates = models.TextField(blank=True)

    soil_type = models.CharField(max_length=50, blank=True)
    ph_level = models.CharField(max_length=50, blank=True)

    irrigation_type = models.CharField(max_length=50, blank=True)
    water_source = models.CharField(max_length=100, blank=True)

    input_costs = models.TextField(blank=True)
    selling_prices = models.TextField(blank=True)

    def __str__(self):
        return self.name or f"Farmer {self.id}"


class Farmer(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    contact = models.CharField(max_length=100, blank=True, null=True)
    crops = models.CharField(max_length=200, blank=True, null=True)


    def __str__(self):
        return self.name


class TransportRequest(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='transport_requests')
    crop = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    pickup = models.CharField(max_length=200)
    dropoff = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='pending')  # pending/assigned/completed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop} ({self.quantity}kg) - {self.farmer.name}"
    
class Transporter(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    current_location = models.CharField(max_length=200)
    load_capacity = models.PositiveIntegerField()  # in kg
    fuel_efficiency = models.FloatField()  # e.g. km/l
    price_per_km = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name    
    
    
    

