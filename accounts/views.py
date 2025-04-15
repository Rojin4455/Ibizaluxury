from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import PropertyData
from accounts.serializers import PropertySerializer
from rest_framework import status
from rest_framework.generics import ListAPIView
from .pagination import PropertyPagination
from accounts.models import PropertyData
from django.db.models import Max, Min
from django.db.models import F


class PropertiesView(ListAPIView):
    queryset = PropertyData.objects.all().order_by('-id')
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]
    pagination_class = PropertyPagination


class FilterView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        min_price = PropertyData.objects.aggregate(min_price=Min('price'))['min_price']
        max_price = PropertyData.objects.aggregate(max_price=Max('price'))['max_price']
        property_types = (
            PropertyData.objects
            .order_by()
            .values_list('property_type', flat=True)
            .distinct()
            .exclude(property_type__isnull=True)
            .exclude(property_type="")
        )        
        property_locations = (
            PropertyData.objects
            .order_by()
            .values_list('town', flat=True)
            .distinct()
            .exclude(town__isnull=True)
            .exclude(town="")
        ) 
        price_freqs = PropertyData.objects.order_by().values_list('price_freq', flat=True).distinct()

        return Response({
            'min_price': min_price,
            'max_price': max_price,
            'property_types': list(property_types),
            'price_freqs': list(price_freqs),
            "locations":list(property_locations),
        })
