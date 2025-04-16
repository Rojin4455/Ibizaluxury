from django.db import models
from django.utils.timezone import now


# Create your models here.
class OAuthToken(models.Model):
    access_token = models.TextField()
    token_type = models.CharField(max_length=100, default="Brearer")
    expires_at = models.DateField() #save this from expires_in
    refresh_token = models.TextField()
    scope = models.TextField()
    userType = models.CharField(max_length=100)
    companyId = models.CharField(max_length=100)
    LocationId = models.CharField(max_length=100)
    userId = models.CharField(max_length=100)
    
    def is_expired(self):
        """Check if the access token is expired"""
        return now().date() >= self.expires_at
    
    def __str__(self):
        return f"{self.LocationId}"
    

class Contact(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    email = models.EmailField(unique=True,blank=True,null=True)
    phone = models.CharField(max_length=50,null=True, blank=True)
    country = models.CharField(max_length=10,null=True, blank=True)
    location_id = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=20, choices=[("lead", "Lead"), ("customer", "Customer")],null=True, blank=True)
    date_added = models.DateTimeField(default=now )  
    date_updated = models.DateTimeField(auto_now=True)  
    dnd = models.BooleanField(default=False)
    min_price = models.CharField(max_length=200, null=True, blank=True)
    max_price = models.CharField(max_length=200, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    price_freq = models.CharField(max_length=50, null=True, blank=True)
    property_type = models.CharField(max_length=100, null=True, blank=True)
    beds = models.IntegerField(null=True, blank=True)
    baths = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class WebhookLog(models.Model):
    webhook_id = models.CharField(max_length=255, unique=True)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.webhook_id} : {self.received_at}"



class CustomField(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    model_name = models.CharField(max_length=50)
    field_key = models.CharField(max_length=255)
    placeholder = models.CharField(max_length=255, blank=True)
    data_type = models.CharField(max_length=50)
    parent_id = models.CharField(max_length=100)
    location_id = models.CharField(max_length=100)
    date_added = models.DateTimeField()

    def __str__(self):
        return self.name