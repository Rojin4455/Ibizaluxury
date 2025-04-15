from django_filters import rest_framework as filters
import django_filters
from .models import PropertyData

property_locations = (
    PropertyData.objects
    .order_by()
    .values_list('town', flat=True)
    .distinct()
    .exclude(town__isnull=True)
    .exclude(town="")
)

class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass

class PropertyDataFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = filters.NumberFilter(field_name="price", lookup_expr='lte')
    property_type = filters.CharFilter(field_name="property_type", lookup_expr='icontains')
    price_freq = filters.CharFilter(field_name="price_freq", lookup_expr='icontains')
    town = filters.MultipleChoiceFilter(
        choices=[(town, town) for town in property_locations],
        conjoined=False,  # OR behavior between selected towns
    )
    beds = filters.NumberFilter(field_name="beds", lookup_expr='exact') 
    baths = filters.NumberFilter(field_name="baths", lookup_expr='exact') 

    class Meta:
        model = PropertyData
        fields = [
            'property_type', 'price_min', 'price_max',
            'price_freq', 'town', 'beds', 'baths'
            ]
