from rest_framework import serializers
from accounts.models import PropertyData


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyData
        fields = '__all__'