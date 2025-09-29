from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
import re
from decimal import Decimal, InvalidOperation


# def get_xml_feed_link_model():
#     from django.apps import apps

#     return apps.get_model('accounts', 'XMLFeedLink')

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
    is_blocked = models.BooleanField(default=False)

    # xml_feeds = models.ManyToManyField(
    #     get_xml_feed_link_model(),
    #     through='XMLFeedSubaccountLink',
    #     related_name='oauth_tokens'
    # )
    
    def __str__(self):
        return f"{self.company_name} ({self.LocationId})"
    
    class Meta:
        verbose_name = "OAuth Token"
        verbose_name_plural = "OAuth Tokens"
    
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

    class Meta:
        ordering = ['-date_added']
    

    def clean_price_value(self, price_str):
        """
        Clean price string and convert to decimal, handling k (thousands) and m (millions)
        Returns None if conversion fails
        
        Examples:
        - "2.3m" -> 2300000
        - "500k" -> 500000
        - "1.5m" -> 1500000
        - "750k" -> 750000
        - "1000000" -> 1000000
        """
        if not price_str:
            return None
        
        # Convert to lowercase string and strip whitespace
        price_str = str(price_str).lower().strip()
        
        # Check for millions (m)
        if price_str.endswith('m'):
            # Extract numeric part
            numeric_part = price_str[:-1]
            try:
                base_value = Decimal(numeric_part)
                return base_value * 1000000  # Convert millions
            except InvalidOperation:
                return None
        
        # Check for thousands (k)
        elif price_str.endswith('k'):
            # Extract numeric part
            numeric_part = price_str[:-1]
            try:
                base_value = Decimal(numeric_part)
                return base_value * 1000  # Convert thousands
            except InvalidOperation:
                return None
        
        # Handle regular numbers (remove any non-numeric characters except decimal points)
        else:
            # Remove currency symbols, commas, etc., but keep decimals
            cleaned = re.sub(r'[^\d.]', '', price_str)
            
            if not cleaned:
                return None
            
            try:
                return Decimal(cleaned)
            except InvalidOperation:
                return None

    @property
    def min_price_decimal(self):
        """Get min_price as decimal value"""
        return self.clean_price_value(self.min_price)
    
    @property
    def max_price_decimal(self):
        """Get max_price as decimal value"""
        return self.clean_price_value(self.max_price)

    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate min_price if provided
        if self.min_price and self.clean_price_value(self.min_price) is None:
            raise ValidationError({'min_price': f'Invalid price format: {self.min_price}'})
        
        # Validate max_price if provided
        if self.max_price and self.clean_price_value(self.max_price) is None:
            raise ValidationError({'max_price': f'Invalid price format: {self.max_price}'})

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