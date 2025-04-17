from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactWebhookView

router = DefaultRouter()



urlpatterns = [
    path("contacts/webhook",ContactWebhookView.as_view(),name ="contact-webhook"),
    path("", include(router.urls)),  
]