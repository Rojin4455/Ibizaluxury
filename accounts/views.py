
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import PropertyData

from rest_framework import status
from rest_framework.generics import ListAPIView
from .pagination import PropertyPagination
from accounts.models import PropertyData
from django.db.models import Max, Min
from django.db.models import F
from rest_framework import viewsets, filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import PropertyData,XMLFeedLink
from .serializers import (
    PropertyDataSerializer, ContactsSerializer,
    XMLFeedSourceSerializer
    )
from .filters import PropertyDataFilter
from core.models import Contact
from django.db.models import Q



class PropertiesView(ListAPIView):
    serializer_class = PropertyDataSerializer
    permission_classes = [AllowAny]
    pagination_class = PropertyPagination

    def get_queryset(self):
        queryset = PropertyData.objects.all().order_by('-id')
        search_val = self.request.query_params.get('search', None)

        if search_val:
            queryset = queryset.filter(
                Q(town__icontains=search_val) |
                Q(features__icontains=search_val) |
                Q(beds__icontains=search_val) |
                Q(baths__icontains=search_val)
            )

        return queryset


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


class PropertyDataPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100
    

class PropertyDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PropertyData.objects.all()
    serializer_class = PropertyDataSerializer
    pagination_class = PropertyDataPagination

    filter_backends = [
        DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    filterset_class = PropertyDataFilter
    search_fields = ['reference', 'town', 'province', 'country', 'description']
    ordering_fields = ['price', 'created_at', 'beds', 'baths', 'built_area', 'plot_area']
    ordering = ['-created_at']



class ContactsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        contacts = Contact.objects.all()
        serializer = ContactsSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class XMLLinkSourceViewSet(viewsets.ModelViewSet):
    queryset = XMLFeedLink.objects.all()
    serializer_class = XMLFeedSourceSerializer
    permission_classes = [AllowAny]