from rest_framework import serializers
from .models import PropertyData

class PropertyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyData
        fields = [
            'id',
            'property_id',
            'reference',
            'price',
            'currency',
            'price_freq',
            'property_type',
            'town',
            'province',
            'country',
            'beds',
            'baths',
            'built_area',
            'plot_area',
            'description',
            'url',
            'features',
            'images',
            'date',
            'created_at',
        ]
