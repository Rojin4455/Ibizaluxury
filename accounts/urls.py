from django.urls import path
from accounts.views import PropertiesView,FilterView
from rest_framework.routers import DefaultRouter
from .views import PropertyDataViewSet

router = DefaultRouter()
router.register(r'properties', PropertyDataViewSet, basename='propertydata')


urlpatterns = [
    path("fetch-properties/",PropertiesView.as_view()),
    path('api/filters/', FilterView.as_view(), name='filter-view'),

]+router.urls

