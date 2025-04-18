from django.urls import path
from accounts.views import PropertiesView,FilterView,XMLLinkSourceViewSet
from rest_framework.routers import DefaultRouter
from .views import PropertyDataViewSet, ContactsView

router = DefaultRouter()
router.register(r'properties', PropertyDataViewSet, basename='propertydata')
router.register(r'xmlfeed', XMLLinkSourceViewSet, basename="xmlfeedsource")


urlpatterns = [
    path("fetch-properties/",PropertiesView.as_view()),
    path('api/filters/', FilterView.as_view(), name='filter-view'),
    path('contacts/', ContactsView.as_view(), name='contact-view'),

]+router.urls

