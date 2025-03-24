from django.db import models

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
