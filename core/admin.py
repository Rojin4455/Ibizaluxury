from django.contrib import admin
from core.models import OAuthToken, Contact
admin.site.register(OAuthToken)
admin.site.register(Contact)