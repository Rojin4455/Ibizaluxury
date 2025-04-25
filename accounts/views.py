
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
    XMLFeedSourceSerializer, ContactSelectionSerializer
    )
from .filters import PropertyDataFilter, ContactFilter
from core.models import Contact
from django.db.models import Q

from core.models import OAuthToken

from accounts.helpers import refresh_xml_feed



class PropertiesView(ListAPIView):
    serializer_class = PropertyDataSerializer
    permission_classes = [AllowAny]
    pagination_class = PropertyPagination

    def get_queryset(self):
        queryset = PropertyData.objects.filter(xml_url__active=True).order_by('-id')
        search_val = self.request.query_params.get('search', None)

        if search_val:
            queryset = queryset.filter(
                Q(town__icontains=search_val) |
                Q(features__icontains=search_val) |
                Q(beds__icontains=search_val) |
                Q(baths__icontains=search_val)
            )

        return queryset





class PropertyDataPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100
    

class PropertyDataViewSet(viewsets.ReadOnlyModelViewSet):
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


    def get_queryset(self):
        queryset = PropertyData.objects.filter(xml_url__active=True)
        xml_url_param = self.request.query_params.get('xml_urls')

        if xml_url_param:
            print("uesss")
            queryset = queryset.filter(xml_url__url=xml_url_param)
        print("u1esss")

        return queryset



class ContactsView(APIView):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactFilter
    
    def get_serializer_class(self, selection=False):
        if selection:
            return ContactSelectionSerializer
        return ContactsSerializer
    
    def filter_queryset(self, request, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)
        return queryset

    def get(self, request, id=None):
        
        selection = request.query_params.get('selection', 'false').lower() in ['true', '1', 'yes']
        serializer_class = self.get_serializer_class(selection)
        
        if id:
            try:
                contact = Contact.objects.get(id=id)
                serializer = serializer_class(contact)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Contact.DoesNotExist:
                return Response({"detail": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            contacts = Contact.objects.all()
            contacts = self.filter_queryset(request, contacts)
            serializer = ContactsSerializer(contacts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id=None):
        
        if not id:
            return Response({"detail": "ID is required for update"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contact = Contact.objects.get(id=id)
        except Contact.DoesNotExist:
            return Response({"detail": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactSelectionSerializer(contact, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)





class FilterView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        queryset = PropertyData.objects.filter(xml_url__active=True)
        min_price = queryset.aggregate(min_price=Min('price'))['min_price']
        max_price = queryset.aggregate(max_price=Max('price'))['max_price']

        property_types = (
            queryset
            .order_by()
            .values_list('property_type', flat=True)
            .distinct()
            .exclude(property_type__isnull=True)
            .exclude(property_type="")
        )

        property_locations = (
            queryset
            .order_by()
            .values_list('town', flat=True)
            .distinct()
            .exclude(town__isnull=True)
            .exclude(town="")
        )

        xml_feeds = (
            queryset
            .order_by()
            .values_list("xml_url__url")
            .distinct()
            
        )

        price_freqs = queryset.order_by().values_list('price_freq', flat=True).distinct()

        return Response({
            'min_price': min_price,
            'max_price': max_price,
            'property_types': list(property_types),
            'price_freqs': list(price_freqs),
            'locations': list(property_locations),
            "xml_urls":list(xml_feeds)
        })



# class ContactsView(APIView):
#     permission_classes = [AllowAny]
    
#     def get_serializer_class(self, selection=False):
#         if selection:
#             return ContactSelectionSerializer
#         return ContactsSerializer
    
#     def get(self, request, id=None):
        
#         selection = request.query_params.get('selection', 'false').lower() in ['true', '1', 'yes']
#         serializer_class = self.get_serializer_class(selection)
        
#         if id:
#             try:
#                 contact = Contact.objects.get(id=id)
#                 serializer = serializer_class(contact)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             except Contact.DoesNotExist:
#                 return Response({"detail": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             contacts = Contact.objects.filter(location_id="ttQIDuvyngILWMJ5wABA")
#             serializer = ContactsSerializer(contacts, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#     def put(self, request, id=None):
        
#         if not id:
#             return Response({"detail": "ID is required for update"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             contact = Contact.objects.get(id=id)
#         except Contact.DoesNotExist:
#             return Response({"detail": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)

#         serializer = ContactSelectionSerializer(contact, data=request.data, partial=True)

#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)

class XMLLinkSourceViewSet(viewsets.ModelViewSet):
    queryset = XMLFeedLink.objects.all()
    serializer_class = XMLFeedSourceSerializer
    permission_classes = [IsAuthenticated]


class EmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = request.data.get("message")
        message = request.data.get("selecdedProps")

        print("message", message)
        return Response()



class CompanyView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, locationId=None):
        if locationId:
            try:
                token = OAuthToken.objects.get(locationId=locationId)
                data = {
                    "companyId": token.companyId,
                    "companyName": token.company_name,
                    "locationId": token.LocationId
                }
                return Response(data, status=status.HTTP_200_OK)
            except OAuthToken.DoesNotExist:
                return Response({"detail": "Token not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            tokens = OAuthToken.objects.all().values("companyId", "company_name","LocationId")
            return Response(list(tokens), status=status.HTTP_200_OK)



class RefreshFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            xml_feed = XMLFeedLink.objects.get(id=id)
            refresh_xml_feed(xml_feed.url)
            return Response({"detail": "Feed refreshed successfully."}, status=status.HTTP_200_OK)
        except XMLFeedLink.DoesNotExist:
            return Response({"detail": "Feed not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubAccountsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        all_accounts = OAuthToken.objects.all().values("companyId", "company_name", "LocationId")
        return Response({
            "status": "success",
            "count": all_accounts.count(),
            "sub_accounts": list(all_accounts)
        })