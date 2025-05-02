from django.db import models
from django.utils import timezone


# def get_sub_accounts_model():
#     from django.apps import apps

#     return apps.get_model('core', 'OAuthToken')


class Property(models.Model):
    property_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    price_freq = models.CharField(max_length=50, null=True, blank=True)
    property_type = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    beds = models.IntegerField(null=True, blank=True)
    baths = models.IntegerField(null=True, blank=True)
    built_area = models.IntegerField(null=True, blank=True)
    plot_area = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    features = models.JSONField(null=True, blank=True)
    images = models.JSONField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference or f"Property {self.property_id}"



class XMLFeedLink(models.Model):
    url = models.URLField(unique=True)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


    subaccounts = models.ManyToManyField(
        'core.OAuthToken',  # Reference the OAuthToken model in the core app
        # through='XMLFeedSubaccount',  # Use the custom through model
        related_name='xml_feeds',  # OAuthToken can access related XMLFeedLinks with this name
    )

    def __str__(self):
        return self.url

    def __str__(self):
        return self.url
    

# class XMLFeedSubaccount(models.Model):
#     xml_feed = models.ForeignKey('accounts.XMLFeedLink', on_delete=models.CASCADE)
#     oauth_token = models.ForeignKey('core.OAuthToken', on_delete=models.CASCADE)
#     added_at = models.DateTimeField(default=timezone.now)
    
#     # Optional: Add additional fields to track relationship details
#     last_synced = models.DateTimeField(null=True, blank=True)
#     sync_enabled = models.BooleanField(default=True)
#     notes = models.TextField(blank=True, null=True)

#     class Meta:
#         # Ensure each subaccount is linked to a feed only once
#         unique_together = ('xml_feed', 'oauth_token')
#         # Optional: Add indexes for better query performance
#         indexes = [
#             models.Index(fields=['xml_feed']),
#             models.Index(fields=['oauth_token']),
#         ]
#         # Set a user-friendly name for the admin interface
#         verbose_name = 'XML Feed Subaccount Access'
#         verbose_name_plural = 'XML Feed Subaccount Access'

#     def __str__(self):
#         return f"{self.xml_feed.url} - {self.oauth_token.company_name or self.oauth_token.LocationId}"
    




class PropertyData(models.Model):
    property_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    price_freq = models.CharField(max_length=50, null=True, blank=True)
    property_type = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    beds = models.IntegerField(null=True, blank=True)
    baths = models.IntegerField(null=True, blank=True)
    built_area = models.IntegerField(null=True, blank=True)
    plot_area = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    features = models.JSONField(null=True, blank=True)
    images = models.JSONField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    xml_url = models.ForeignKey(XMLFeedLink, on_delete=models.CASCADE, related_name='xmlfeedlink', null=True, blank=True)


    class Meta:
        db_table = 'propertydata'


    def __str__(self):
        return self.reference or f"Property {self.property_id}"

