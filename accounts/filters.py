from django_filters import rest_framework as filters
import django_filters
from django.db.models import Q
from .models import PropertyData
from core.models import Contact
from .helpers import (
    clean_price_value,
    property_price_freq_q_rental,
    property_price_freq_q_sale,
)

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
    # CharFilter + method so values like "12k", "2.3m", "1.500.000" parse like contact prices
    price_min = django_filters.CharFilter(method="filter_price_min")
    price_max = django_filters.CharFilter(method="filter_price_max")
    price_freq = filters.CharFilter(field_name="price_freq", lookup_expr='icontains')
    # Comma-separated: sale, rental — OR match on PropertyData.price_freq (aligns with contact tags)
    price_freq_modes = django_filters.CharFilter(method="filter_price_freq_modes")
    town = CharInFilter(field_name="town", lookup_expr="in")
    province = filters.CharFilter(field_name="province", lookup_expr="icontains")

    # town = django_filters.MultipleChoiceFilter(
    #     field_name="town",
    #     choices=[],   # empty at import time
    #     conjoined=False,  # OR behavior between selected towns
    # )

    beds = filters.NumberFilter(method='filter_beds')
    baths = filters.NumberFilter(method='filter_baths')
    xml_url = filters.CharFilter(field_name='xml_url__url', lookup_expr='exact')
    currency = filters.CharFilter(field_name='currency', lookup_expr='exact')

    property_type = filters.CharFilter(method="filter_property_type")

    class Meta:
        model = PropertyData
        fields = [
            'property_type', 'price_min', 'price_max',
            'price_freq', 'price_freq_modes', 'town', 'province', 'beds', 'baths', 'xml_url', 'currency'
            ]

    def filter_price_min(self, queryset, name, value):
        if value is None or not str(value).strip():
            return queryset
        parsed = clean_price_value(value)
        if parsed is None:
            return queryset
        return queryset.filter(price__gte=parsed)

    def filter_price_max(self, queryset, name, value):
        if value is None or not str(value).strip():
            return queryset
        parsed = clean_price_value(value)
        if parsed is None:
            return queryset
        return queryset.filter(price__lte=parsed)

    def filter_price_freq_modes(self, queryset, name, value):
        if value is None or not str(value).strip():
            return queryset
        modes = {x.strip().lower() for x in str(value).split(",") if x.strip()}
        q_main = Q()
        if "sale" in modes:
            q_main |= property_price_freq_q_sale()
        if "rental" in modes:
            q_main |= property_price_freq_q_rental()
        return queryset.filter(q_main) if q_main else queryset

    def filter_beds(self, queryset, name, value):
        if value >= 4:
            return queryset.filter(**{f"{name}__gte": value})
        return queryset.filter(**{name: value})

    def filter_baths(self, queryset, name, value):
        if value >= 4:
            return queryset.filter(**{f"{name}__gte": value})
        return queryset.filter(**{name: value})
    

    def filter_property_type(self, queryset, name, value):
        allowed = ["land", "villa", "appartment", "finca"]
        if value and value.lower() in [x.lower() for x in allowed]:
            return queryset.filter(**{f"{name}__iexact": value})
        return queryset  # ignore if not in allowed list



class ContactFilter(filters.FilterSet):
    location_id = filters.CharFilter(lookup_expr='exact')
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Contact
        fields = ['location_id']

    def filter_search(self, queryset, name, value):
        if not value or not value.strip():
            return queryset
        q = value.strip()
        return queryset.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )


