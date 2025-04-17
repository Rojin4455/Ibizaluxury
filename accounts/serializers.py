from rest_framework import serializers
from .models import PropertyData,XMLFeedLink
from core.models import Contact
import requests
import xml.etree.ElementTree as ET

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



class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
        
class XMLFeedSourceSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(required=False)

    class Meta:
        model = XMLFeedLink
        fields = [
            "id",
            "url",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")


    def create(self, validated_data):
        validated_data["active"] = True
        return super().create(validated_data)

    
    # def validate_url(self, value):
    #     # Try fetching the URL
    #     try:
    #         response = requests.get(value, timeout=10)
    #         response.raise_for_status()  # Raise HTTP errors

    #         # Parse XML
    #         root = ET.fromstring(response.content)

    #         # Check if at least one <property> exists
    #         if not root.findall(".//property"):
    #             raise serializers.ValidationError(
    #                 "The provided URL does not contain any <property> elements."
    #             )

    #     except (requests.RequestException, ET.ParseError) as e:
    #         raise serializers.ValidationError(
    #             f"Invalid or inaccessible XML feed URL: {str(e)}"
    #         )

    #     return value