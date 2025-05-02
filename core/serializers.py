from rest_framework import serializers
from core.models import Contact, OAuthToken



class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthToken
        # fields = "__all__"
        fields = ['company_name', 'is_blocked', 'LocationId', 'id'] 