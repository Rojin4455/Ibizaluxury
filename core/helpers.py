from core.models import CustomField, OAuthToken
import requests
from datetime import datetime
import re


def map_to_customfield(custom_field_id, location_id):
    custom_field = CustomField.objects.filter(id = custom_field_id, location_id = location_id)
    if custom_field:
        return custom_field.first()
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


def _to_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def _parse_price_number(raw):
    if raw is None:
        return None
    text = str(raw).strip().replace(",", "")
    if not text:
        return None

    # Normalize thousand separators such as 750.000
    if text.count(".") > 1:
        text = text.replace(".", "")
    elif text.count(".") == 1:
        left, right = text.split(".")
        if len(right) == 3 and left.isdigit() and right.isdigit():
            text = left + right

    cleaned = re.sub(r"[^\d.]", "", text)
    if not cleaned:
        return None

    try:
        return int(float(cleaned))
    except ValueError:
        return None


def _extract_price_bounds(values):
    lows = []
    highs = []
    for value in _to_list(values):
        if "-" in value:
            low_raw, high_raw = value.split("-", 1)
            low = _parse_price_number(low_raw)
            high = _parse_price_number(high_raw)
            if low is not None:
                lows.append(low)
            if high is not None:
                highs.append(high)
        else:
            point = _parse_price_number(value)
            if point is not None:
                lows.append(point)
                highs.append(point)
    if not lows or not highs:
        return None, None
    return min(lows), max(highs)


def normalize_contact_custom_fields(fields):
    """
    Convert GHL custom-field names to canonical Contact fields.
    Keeps raw values for reporting and derives values used for filtering.
    """
    data = {str(k).lower(): v for k, v in (fields or {}).items()}
    normalized = {}

    property_type_list = _to_list(data.get("property type") or data.get("property_type"))
    rental_type_list = _to_list(data.get("rental property type"))
    budget_ranges = _to_list(data.get("budget"))
    weekly_ranges = _to_list(data.get("weekly price range"))

    preferred_location = (
        data.get("prefered location")
        or data.get("preferred location")
        or data.get("province")
    )
    beds = data.get("number of bedrooms", data.get("beds"))
    baths = data.get("number of bathrooms", data.get("baths"))

    is_rental = bool(rental_type_list or weekly_ranges)
    is_sale = bool(budget_ranges) and not is_rental
    property_status = "rental" if is_rental else ("sale" if is_sale else None)

    price_min = data.get("min_price")
    price_max = data.get("max_price")
    price_freq = data.get("price_freq")

    if is_rental:
        min_v, max_v = _extract_price_bounds(weekly_ranges)
        if min_v is not None:
            price_min = str(min_v)
        if max_v is not None:
            price_max = str(max_v)
        price_freq = "week"
    elif is_sale:
        min_v, max_v = _extract_price_bounds(budget_ranges)
        if min_v is not None:
            price_min = str(min_v)
        if max_v is not None:
            price_max = str(max_v)

    normalized.update({
        "property_type": ", ".join(property_type_list) if property_type_list else data.get("property_type"),
        "province": preferred_location,
        "beds": beds,
        "baths": baths,
        "min_price": price_min,
        "max_price": price_max,
        "price_freq": price_freq,
        "preferred_location": preferred_location,
        "budget": ", ".join(budget_ranges) if budget_ranges else None,
        "weekly_price_range": ", ".join(weekly_ranges) if weekly_ranges else None,
        "rental_property_type": ", ".join(rental_type_list) if rental_type_list else None,
        "checkin_date": data.get("checkin date"),
        "checkout_date": data.get("checkout date"),
        "property_status": property_status,
    })

    return normalized
