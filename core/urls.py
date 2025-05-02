from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactWebhookView, TokenView, LocationListCreateDeleteView

router = DefaultRouter()



urlpatterns = [
    path("contacts/webhook",ContactWebhookView.as_view(),name ="contact-webhook"),
    path("", include(router.urls)),
    path('tokens', TokenView.as_view()),
    path('locations/', LocationListCreateDeleteView.as_view(), name='locations-list'),
    path('locations/<int:pk>/delete/', LocationListCreateDeleteView.as_view(), name='location-delete'),
    path('locations/<int:pk>/toggle-status/', LocationListCreateDeleteView.as_view(), name='location-toggle-status'),
]