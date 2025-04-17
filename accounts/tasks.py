import xml.etree.ElementTree as ET
import requests
from django.utils.dateparse import parse_datetime
from accounts.models import Property,PropertyData,XMLFeedLink
from celery import shared_task
from django.db import transaction


@shared_task
def handle_xmlfeed():
    
    feed_links = XMLFeedLink.objects.filter(active=True)
    
    xml_property_ids = set()
    with transaction.atomic():
        for feed_link in feed_links:
            # xml_url = "https://ibizaluxuryxl.com/kyero-xmlfeed/"
            xml_url = feed_link.url
            try:
                response = requests.get(xml_url)
                root = ET.fromstring(response.content)
                
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

                
                
            except Exception as e:
                print(f"Error while processing {xml_url}: {e} ")
        db_property_ids = set(Property.objects.values_list("property_id", flat=True))

        properties_to_delete = db_property_ids - xml_property_ids
        if properties_to_delete:
            Property.objects.filter(property_id__in=properties_to_delete).delete()
                

def sample():
    xml_url = "https://ibizaluxuryxl.com/rental-sale-xmlfeed/"
    response = requests.get(xml_url)
    root = ET.fromstring(response.content)
    xml_property_ids = set()
    print("len od property", len(root.findall(".//property")) )

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
                "images": [img.find("url").text for img in property_elem.findall(".//images/image") if img.find("url") is not None],
                "date": get_datetime(property_elem, "date"),
            }

            PropertyData.objects.update_or_create(property_id=property_data["property_id"], defaults=property_data)

        
    db_property_ids = set(PropertyData.objects.values_list("property_id", flat=True))

    properties_to_delete = db_property_ids - xml_property_ids

    PropertyData.objects.filter(property_id__in=properties_to_delete).delete()

        

import requests
import xml.etree.ElementTree as ET
from django.db import transaction
from django.db.models import Q
from typing import List, Dict, Set

def parse_property_data(property_elem) -> Dict:
    """
    Parse individual property element and extract relevant data.
    
    Args:
        property_elem (xml.etree.ElementTree.Element): XML property element
    
    Returns:
        Dict: Parsed property data
    """
    return {
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
        "images": [img.find("url").text for img in property_elem.findall(".//images/image") if img.find("url") is not None],
        "date": get_datetime(property_elem, "date"),
    }

@transaction.atomic
def import_properties_from_xml():
    """
    Efficiently import properties from XML feed using bulk operations.
    
    Key Optimizations:
    - Bulk create/update
    - Single database transaction
    - Minimal database queries
    - Efficient property tracking
    """
    # Fetch XML data
    xml_url = "https://ibizaluxuryxl.com/rental-sale-xmlfeed/"
    response = requests.get(xml_url)
    root = ET.fromstring(response.content)
    
    # Parse all property elements
    property_elements = root.findall(".//property")
    print(f"Total properties in XML: {len(property_elements)}")
    
    # # Parse and prepare property data
    property_data_list: List[Dict] = []
    xml_property_ids: Set[str] = set()
    
    for property_elem in property_elements:
        property_data = parse_property_data(property_elem)
        property_data_list.append(property_data)
        xml_property_ids.add(property_data['property_id'])
    
    # Bulk create or update properties
    property_objs_to_create = []
    property_objs_to_update = []
    
    # Retrieve existing properties in a single query
    existing_properties = PropertyData.objects.filter(
        property_id__in=xml_property_ids
    ).in_bulk(field_name='property_id')
    
    for property_data in property_data_list:
        property_id = property_data['property_id']
        
        if property_id in existing_properties:
            # Update existing property
            existing_obj = existing_properties[property_id]
            for key, value in property_data.items():
                setattr(existing_obj, key, value)
            property_objs_to_update.append(existing_obj)
        else:
            # Create new property object
            property_objs_to_create.append(
                PropertyData(**property_data)
            )
    
    # Bulk update existing properties
    if property_objs_to_update:
        PropertyData.objects.bulk_update(
            property_objs_to_update, 
            fields=[
                'reference', 'price', 'currency', 'price_freq', 
                'property_type', 'town', 'province', 'country', 
                'beds', 'baths', 'built_area', 'plot_area', 
                'description', 'url', 'features', 'images', 'date'
            ]
        )
    
    # Bulk create new properties
    if property_objs_to_create:
        PropertyData.objects.bulk_create(property_objs_to_create)
    
    # Delete properties not in XML
    db_property_ids = set(PropertyData.objects.values_list("property_id", flat=True))
    properties_to_delete = db_property_ids - xml_property_ids
    
    if properties_to_delete:
        PropertyData.objects.filter(property_id__in=properties_to_delete).delete()
    
    print(f"Created: {len(property_objs_to_create)} properties")
    print(f"Updated: {len(property_objs_to_update)} properties")
    print(f"Deleted: {len(properties_to_delete)} properties")

@shared_task
def import_properties_with_retry(max_retries=3):
    """
    Import properties with retry mechanism and error handling.
    """
    for attempt in range(max_retries):
        try:
            import_properties_from_xml()
            break
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise




            

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


from django.utils.timezone import make_aware
import datetime

def get_datetime(element, tag):
    date_str = element.find(tag).text if element.find(tag) is not None else None
    if date_str:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return make_aware(dt)
    return None