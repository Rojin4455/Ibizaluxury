from django.urls import path
from accounts.views import PropertiesView,FilterView

urlpatterns = [
    path("fetch-properties/",PropertiesView.as_view()),
    path('api/filters/', FilterView.as_view(), name='filter-view'),

]