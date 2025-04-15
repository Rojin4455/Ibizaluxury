from django_filters import rest_framework as filters
from .models import PropertyData

class PropertyDataFilter(filters.FilterSet):
    price_from = filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_to = filters.NumberFilter(field_name="price", lookup_expr='lte')
    property_type = filters.CharFilter(field_name="property_type", lookup_expr='icontains')

    class Meta:
        model = PropertyData
        fields = ['property_type', 'price_from', 'price_to']
