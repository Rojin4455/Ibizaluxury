import xml.etree.ElementTree as ET
import requests
from django.utils.dateparse import parse_datetime
from accounts.models import Property,PropertyData,XMLFeedLink
from accounts.helpers import refresh_xml_feed
from celery import shared_task
from django.db import transaction


@shared_task
def handle_xmlfeed():
    
    feed_links = XMLFeedLink.objects.filter(active=True)
    for feed_link in feed_links:
        refresh_xml_feed(feed_link.url)