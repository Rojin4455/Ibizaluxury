from django_filters import rest_framework as filters
import django_filters
from .models import PropertyData


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass

class PropertyDataFilter(filters.FilterSet):
    price_from = filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_to = filters.NumberFilter(field_name="price", lookup_expr='lte')
    property_type = filters.CharFilter(field_name="property_type", lookup_expr='icontains')
    price_freq = filters.CharFilter(field_name="price_freq", lookup_expr='icontains')
    town = CharInFilter(field_name="town", lookup_expr='in')
    beds = filters.NumberFilter(field_name="beds", lookup_expr='exact') 
    baths = filters.NumberFilter(field_name="baths", lookup_expr='exact') 

    class Meta:
        model = PropertyData
        fields = [
            'property_type', 'price_from', 'price_to',
            'price_freq', 'town', 'beds', 'baths'
            ]
