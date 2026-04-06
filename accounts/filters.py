from decimal import Decimal

from django_filters import rest_framework as filters
import django_filters
from django.db.models import F, Q, TextField, Value, DecimalField
from django.db.models.functions import Cast, Coalesce

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
    location_id = filters.CharFilter(lookup_expr="exact")
    search = filters.CharFilter(method="filter_search")
    # all | sale | rental | both — matches tags, property_status, price_freq
    listing_type = django_filters.CharFilter(method="filter_listing_type")
    contact_price_min = django_filters.CharFilter(method="filter_contact_price_bounds")
    contact_price_max = django_filters.CharFilter(method="filter_contact_price_bounds")
    # Free text: villa, apartment, etc. (matches property_type and rental_property_type)
    contact_property_type = django_filters.CharFilter(method="filter_contact_property_type")

    class Meta:
        model = Contact
        fields = ["location_id"]

    def filter_search(self, queryset, name, value):
        if not value or not value.strip():
            return queryset
        q = value.strip()
        return queryset.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
            | Q(phone__icontains=q)
        )

    def filter_listing_type(self, queryset, name, value):
        v = (value or "").strip().lower()
        if not v or v == "all":
            return queryset

        qs = queryset.annotate(_listing_tags_txt=Cast(F("tags"), output_field=TextField()))
        q_sale = (
            Q(property_status__iexact="sale")
            | Q(price_freq__iexact="sale")
            | Q(price_freq__icontains="sale")
            | Q(_listing_tags_txt__icontains="sale")
        )
        q_rental = (
            Q(property_status__iexact="rental")
            | Q(price_freq__iexact="week")
            | Q(price_freq__icontains="week")
            | Q(price_freq__icontains="rental")
            | Q(_listing_tags_txt__icontains="rental")
        )
        if v == "sale":
            return qs.filter(q_sale)
        if v == "rental":
            return qs.filter(q_rental)
        if v == "both":
            return qs.filter(q_sale & q_rental)
        return queryset

    def filter_contact_price_bounds(self, queryset, name, value):
        # django-filter invokes this for both contact_price_min and contact_price_max
        if getattr(self, "_contact_price_bounds_applied", False):
            return queryset
        self._contact_price_bounds_applied = True

        pmin = clean_price_value(self.data.get("contact_price_min"))
        pmax = clean_price_value(self.data.get("contact_price_max"))
        if pmin is None and pmax is None:
            return queryset

        floor = pmin if pmin is not None else Decimal(0)
        ceiling = pmax if pmax is not None else Decimal("999999999999999")
        dec = DecimalField(max_digits=20, decimal_places=2)
        open_hi = Decimal("999999999999999")

        return queryset.annotate(
            _cb_lo=Coalesce("min_price_value", Value(Decimal(0)), output_field=dec),
            _cb_hi=Coalesce("max_price_value", Value(open_hi), output_field=dec),
        ).filter(_cb_lo__lte=ceiling, _cb_hi__gte=floor)

    def filter_contact_property_type(self, queryset, name, value):
        if not value or not str(value).strip():
            return queryset
        v = str(value).strip()
        if v.lower() == "all":
            return queryset
        return queryset.filter(
            Q(property_type__icontains=v) | Q(rental_property_type__icontains=v)
        )


