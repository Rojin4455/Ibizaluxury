from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser


# Create your models here.
# class User(AbstractUser):
#     username = models.CharField(max_length=150, unique=True, blank=True, null=True)
#     email = models.EmailField(unique=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     def __str__(self):
#         return self.email


class OAuthToken(models.Model):
    access_token = models.TextField()
    token_type = models.CharField(max_length=100, default="Brearer")
    expires_at = models.DateField()
    refresh_token = models.TextField()
    scope = models.TextField()
    userType = models.CharField(max_length=100)
    companyId = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    LocationId = models.CharField(max_length=100,unique=True)
    userId = models.CharField(max_length=100)
    
    def is_expired(self):
        """Check if the access token is expired"""
        return now().date() >= self.expires_at
    
    def __str__(self):
        return f"{self.LocationId} - {self.token_type}"
    

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
    properties = models.ManyToManyField('accounts.PropertyData', blank=True, related_name="contacts")
    remarks = models.TextField(null=True, blank=True)
    selec_url = models.URLField(null=True, blank=True)
    

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