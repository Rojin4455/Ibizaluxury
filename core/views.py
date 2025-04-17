from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from .models import Contact, WebhookLog

import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from core import helpers

# Create your views here.
logger = logging.getLogger(__name__)
def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
    
class ContactPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = "page_size"
    max_page_size = 50  # Limit max page size

# Contact ViewSet



@method_decorator(csrf_exempt, name='dispatch')
class ContactWebhookView(APIView):
    """
    Handles incoming webhook events from GoHighLevel.
    """
    permission_classes = [AllowAny]
    def get(self,request):
        return Response({"webhook get": "Webhook get page"}, status=status.HTTP_200_OK)
        
    def post(self, request):
        """
        Process webhook events.
        """
        payload = request.data
        print("asdf",payload)
        webhook_id = payload.get("webhookId")
        event_type = payload.get("type")
        customfields = self.add_customfields(payload.get("customFields",None),payload.get("locationId",None))
        contact_data = {
            "id":payload.get("id"),
            "firstName":payload.get("firstName",""),
            "lastName":payload.get("lastName",""),
            "email":payload.get("email"),
            "phone":payload.get("phone",""),
            **customfields
            
            }

        if WebhookLog.objects.filter(webhook_id=webhook_id).exists():
            return Response({"error": "Duplicate webhook detected"}, status=status.HTTP_409_CONFLICT)
        
        # Log webhook
        WebhookLog.objects.create(webhook_id=webhook_id, received_at=now())

        print(f"\nwebhook: {webhook_id} \npayload :",contact_data,event_type)
        # Process events
        if event_type == "ContactCreate":
            self.create_contact(contact_data)
        elif event_type == "ContactDelete":
            self.delete_contact(contact_data)
        elif event_type == "ContactUpdate":
            self.update_contact(contact_data)
        # elif event_type == "ContactDndUpdate":
        #     self.update_contact_dnd(contact_data)
        # elif event_type == "ContactTagUpdate":
        #     self.update_contact_tags(contact_data)
        # elif event_type == "NoteCreate":
        #     self.create_note(contact_data)
        # elif event_type == "NoteDelete":
        #     self.delete_note(contact_data)
        # elif event_type == "TaskCreate":
        #     self.create_task(contact_data)
        # elif event_type == "TaskDelete":
        #     self.delete_task(contact_data)

        return Response({"message": "Webhook processed successfully"}, status=status.HTTP_200_OK)
    
    def add_customfields(self, data, locatioId):
        cf_dict={}
        if data and locatioId:
            for cf in data:
                print("cf",cf)
                cf_obj = helpers.map_to_customfield(cf["id"],locatioId)
                cf_dict[cf_obj.name.lower()]=cf["value"]
        # print("added custom fields: ", cf_dict)     
        return cf_dict
    
    def create_contact(self, data):
        """ Creates a new contact """
        Contact.objects.create(
            id=data["id"],
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            min_price = data.get("min_price",""),
            max_price = data.get("max_price",""),
            province = data.get("province",""),
            price_freq = data.get("price_freq",""),
            property_type = data.get("property_type",""),
            beds = safe_int(data.get("beds")),
            baths = safe_int(data.get("baths"))
        )
    
    def update_contact(self, data):
        """ Updates a contact """
        contact = Contact.objects.filter(id=data["id"]).first()
        if contact:
            contact.first_name = data.get("firstName", contact.first_name)
            contact.last_name = data.get("lastName", contact.last_name)
            contact.email = data.get("email", contact.email)
            contact.phone = data.get("phone", contact.phone)
            contact.min_price = data.get("min_price", contact.min_price)
            contact.max_price = data.get("max_price", contact.max_price)
            contact.province = data.get("province", contact.province)
            contact.price_freq = data.get("price_freq", contact.price_freq)
            contact.property_type = data.get("property_type", contact.property_type)
            contact.beds = int(data.get("beds", contact.beds))
            contact.baths = int(data.get("baths", contact.baths))
            contact.save()
            logger.info(f"Updated contact: {data['id']}")
        else:
            logger.warning(f"Contact {data['id']} not found for update")

    def delete_contact(self, data):
        """ Deletes a contact """
        Contact.objects.filter(id=data["id"]).delete()