from rest_framework import serializers
from .models import Farmer
from .models import TransportRequest
from .models import FarmerProfile

class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = '__all__'

class TransportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportRequest
        fields = '__all__'

class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = '__all__'
