from django.urls import path
from accounts.views import PropertiesView,FilterView,XMLLinkSourceViewSet
from rest_framework.routers import DefaultRouter
from .views import PropertyDataViewSet, ContactsView, EmailView, CompanyView, RefreshFeedView, SubAccountsView, AddSubaccountToXMLFeedView

router = DefaultRouter()
router.register(r'properties', PropertyDataViewSet, basename='propertydata')
router.register(r'xmlfeed', XMLLinkSourceViewSet, basename="xmlfeedsource")


urlpatterns = [
    path("fetch-properties/",PropertiesView.as_view()),
    path('api/filters/', FilterView.as_view(), name='filter-view'),
    path('contacts/<str:id>', ContactsView.as_view(), name='contact-view'),
    path('contacts/', ContactsView.as_view()),
    path('send-email/', EmailView.as_view(), name='email-view'),
    path('get-company-names/', CompanyView.as_view(), name='get-company-name'),
    path('get-company-name/<str:locationId>/', CompanyView.as_view(), name='get-company-name'),
    path('refresh-feed/<int:id>/', RefreshFeedView.as_view()),
    path('fetch-accounts/', SubAccountsView.as_view()),
    path('xmlfeeds/<int:pk>/add-subaccounts/', AddSubaccountToXMLFeedView.as_view(), name='add-subaccounts'),

]+router.urls

