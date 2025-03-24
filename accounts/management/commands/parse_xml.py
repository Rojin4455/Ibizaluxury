import xml.etree.ElementTree as ET
import requests
from django.utils.dateparse import parse_datetime
from django.core.management.base import BaseCommand
from accounts.models import Property

class Command(BaseCommand):
    help = "Parse XML feed and store property data in the database"

    def handle(self, *args, **kwargs):
        xml_url = "https://ibizaluxuryxl.com/kyero-xmlfeed/"
        response = requests.get(xml_url)
        root = ET.fromstring(response.content)

        for property_elem in root.findall(".//property"):
            property_data = {
                "property_id": self.get_text(property_elem, "id"),
                "reference": self.get_text(property_elem, "ref"),
                "price": self.get_decimal(property_elem, "price"),
                "currency": self.get_text(property_elem, "currency"),
                "price_freq": self.get_text(property_elem, "price_freq"),
                "property_type": self.get_text(property_elem, "type"),
                "town": self.get_text(property_elem, "town"),
                "province": self.get_text(property_elem, "province"),
                "country": self.get_text(property_elem, "country"),
                "beds": self.get_int(property_elem, "beds"),
                "baths": self.get_int(property_elem, "baths"),
                "built_area": self.get_int(property_elem, "surface_area/built"),
                "plot_area": self.get_int(property_elem, "surface_area/plot"),
                "description": self.get_text(property_elem, "desc/en"),
                "url": self.get_text(property_elem, "url/en"),
                "features": [feature.text for feature in property_elem.findall(".//features/feature")],
                "images": [img.find("url").text for img in property_elem.findall(".//images/image")],
                "date": self.get_datetime(property_elem, "date"),
            }

            Property.objects.update_or_create(property_id=property_data["property_id"], defaults=property_data)

        self.stdout.write(self.style.SUCCESS("XML data successfully parsed and stored!"))

    @staticmethod
    def get_text(element, path):
        tag = element.find(path)
        return tag.text if tag is not None else None

    @staticmethod
    def get_int(element, path):
        tag = element.find(path)
        return int(tag.text) if tag is not None and tag.text.isdigit() else None

    @staticmethod
    def get_decimal(element, path):
        tag = element.find(path)
        try:
            return float(tag.text) if tag is not None else None
        except ValueError:
            return None

    @staticmethod
    def get_datetime(element, path):
        tag = element.find(path)
        return parse_datetime(tag.text) if tag is not None else None
