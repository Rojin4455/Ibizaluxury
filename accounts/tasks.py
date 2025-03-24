import xml.etree.ElementTree as ET
import requests
from django.utils.dateparse import parse_datetime
from accounts.models import Property
from celery import shared_task


@shared_task
def handle_xmlfeed():
        xml_url = "https://ibizaluxuryxl.com/kyero-xmlfeed/"
        response = requests.get(xml_url)
        root = ET.fromstring(response.content)
        xml_property_ids = set()  # To store property IDs from XML feed

        for property_elem in root.findall(".//property"):
            property_id = get_text(property_elem, "id")
            xml_property_ids.add(property_id) 
            property_data = {
                "property_id": get_text(property_elem, "id"),
                "reference": get_text(property_elem, "ref"),
                "price": get_decimal(property_elem, "price"),
                "currency": get_text(property_elem, "currency"),
                "price_freq": get_text(property_elem, "price_freq"),
                "property_type": get_text(property_elem, "type"),
                "town": get_text(property_elem, "town"),
                "province": get_text(property_elem, "province"),
                "country": get_text(property_elem, "country"),
                "beds": get_int(property_elem, "beds"),
                "baths": get_int(property_elem, "baths"),
                "built_area": get_int(property_elem, "surface_area/built"),
                "plot_area": get_int(property_elem, "surface_area/plot"),
                "description": get_text(property_elem, "desc/en"),
                "url": get_text(property_elem, "url/en"),
                "features": [feature.text for feature in property_elem.findall(".//features/feature")],
                "images": [img.find("url").text for img in property_elem.findall(".//images/image")],
                "date": get_datetime(property_elem, "date"),
            }

            Property.objects.update_or_create(property_id=property_data["property_id"], defaults=property_data)

        
        db_property_ids = set(Property.objects.values_list("property_id", flat=True))

        properties_to_delete = db_property_ids - xml_property_ids

        Property.objects.filter(property_id__in=properties_to_delete).delete()

        


def get_text(element, path):
    tag = element.find(path)
    return tag.text if tag is not None else None


def get_int(element, path):
    tag = element.find(path)
    return int(tag.text) if tag is not None and tag.text.isdigit() else None


def get_decimal(element, path):
    tag = element.find(path)
    try:
        return float(tag.text) if tag is not None else None
    except ValueError:
        return None


def get_datetime(element, path):
    tag = element.find(path)
    return parse_datetime(tag.text) if tag is not None else None