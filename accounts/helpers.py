from core.models import CustomField, OAuthToken
from accounts.models import XMLFeedLink, PropertyData
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


def map_to_customfield(custom_field_id, location_id):
    custom_field = CustomField.objects.get(id = custom_field_id, location_id = location_id)
    if custom_field:
        return custom_field
    else:
        custom_field = save_custom_field_to_db(custom_field_id, location_id)
        return custom_field


def save_custom_field_to_db(custom_field_id, location_id):
    token = OAuthToken.objects.filter(LocationId=location_id).first()
    
    if not token:
        print("No token found for location.")
        return None

    response = get_custom_field(location_id, custom_field_id, token.access_token)

    if response and response.get("customField"):
        data = response["customField"]
        
        custom_field, created = CustomField.objects.update_or_create(
            id=data["id"],
            defaults={
                "name": data["name"],
                "model_name": data["model"],
                "field_key": data["fieldKey"],
                "placeholder": data.get("placeholder", ""),
                "data_type": data["dataType"],
                "parent_id": data["parentId"],
                "location_id": data["locationId"],
                "date_added": datetime.fromisoformat(data["dateAdded"].replace("Z", "+00:00")),
            }
        )

        if created:
            print(f"Custom field '{custom_field.name}' created.")
        else:
            print(f"Custom field '{custom_field.name}' updated.")

        return custom_field
    else:
        print("Custom field data not found.")
        return None


def get_custom_field(location_id, field_id, access_token):

    url = f"https://services.leadconnectorhq.com/locations/{location_id}/customFields/{field_id}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Version": "2021-07-28"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None



from django.db import transaction
from django.db.models import Q

def refresh_xml_feed(url):
    feed_link = XMLFeedLink.objects.filter(url=url).first()
    if not feed_link:
        return

    xml_property_ids = set()
    xml_url = feed_link.url

    try:
        response = requests.get(xml_url)
        root = ET.fromstring(response.content)

        properties_to_create = []
        properties_to_update = []
        property_id_map = {}
        current_properties = PropertyData.objects.filter(xml_url=feed_link).in_bulk(field_name="property_id")
        other_current_properties = PropertyData.objects.exclude(property_id__in=current_properties).in_bulk(field_name="property_id")        
 
        # print("len of data: ", len(root.findall(".//property")))

        for property_elem in root.findall(".//property"):
            property_id = get_text(property_elem, "id")
            if not property_id:
                continue

            # print("property_id:", property_id, end=" -> ")

            xml_property_ids.add(property_id)

            property_data = {
                "property_id": property_id,
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
                "images": [
                    img.find("url").text
                    for img in property_elem.findall(".//images/image")
                    if img.find("url") is not None and img.find("url").text
                ],
                "date": get_datetime(property_elem, "date"),
                "xml_url":feed_link
            }
            if property_id in other_current_properties:
                continue

            if property_id in current_properties:
                print("property_id: -> ", property_id)
                prop = current_properties[property_id]
                for field, value in property_data.items():
                    setattr(prop, field, value)
                properties_to_update.append(prop)
            else:
                properties_to_create.append(PropertyData(**property_data))

        # Bulk update and create
        with transaction.atomic():
            if properties_to_create:
                PropertyData.objects.bulk_create(properties_to_create, batch_size=100)
            if properties_to_update:
                PropertyData.objects.bulk_update(properties_to_update, [
                    "reference", "price", "currency", "price_freq", "property_type", "town", "province",
                    "country", "beds", "baths", "built_area", "plot_area", "description", "url", "features",
                    "images", "date", 'xml_url'
                ], batch_size=100)

    except Exception as e:
        print(f"Error while processing {xml_url}: {e}")
        return

    # Delete obsolete properties
    db_property_ids = set(PropertyData.objects.filter(xml_url=feed_link).values_list("property_id", flat=True))
    properties_to_delete = db_property_ids - xml_property_ids
    if properties_to_delete:
        PropertyData.objects.filter(property_id__in=properties_to_delete).delete()


def get_text(element, path):
    tag = element.find(path)
    return tag.text.strip() if tag is not None and tag.text else None



def get_int(element, path):
    tag = element.find(path)
    try:
        return int(tag.text.strip()) if tag is not None and tag.text else None
    except (ValueError, AttributeError):
        return None


def get_decimal(element, path):
    tag = element.find(path)
    try:
        return float(tag.text.strip()) if tag is not None and tag.text else None
    except (ValueError, AttributeError):
        return None



from django.utils.timezone import make_aware
import datetime

def get_datetime(element, path):
    tag = element.find(path)
    date_str = tag.text.strip() if tag is not None and tag.text else None
    try:
        if date_str:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return make_aware(dt)
    except ValueError:
        return None
    return None