from rest_framework import serializers
from .models import PropertyData,XMLFeedLink
from core.models import Contact, CustomField, OAuthToken
from core.services import ContactServices
import requests
import xml.etree.ElementTree as ET
from core.serializers import LocationSerializer
from accounts.helpers import refresh_xml_feed
from accounts.tasks import handle_refresh_xmlfeed_each


class PropertyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyData
        fields = [
            'id',
            'property_id',
            'reference',
            'price',
            'currency',
            'price_freq',
            'property_type',
            'town',
            'province',
            'country',
            'beds',
            'baths',
            'built_area',
            'plot_area',
            'description',
            'url',
            'features',
            'images',
            'date',
            'created_at',
            'xml_url',
        ]



class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        # fields = "__all__"
        exclude = ['remarks', 'selec_url', 'is_active']


class ContactSelectionSerializer(serializers.ModelSerializer):
    properties_detail = PropertyDataSerializer(source="properties", many=True, read_only=True)
    properties = serializers.PrimaryKeyRelatedField(
        queryset=PropertyData.objects.filter(xml_url__active=True),
        many=True,
        write_only=True,
    )
    last_shared_property_ids = serializers.JSONField(read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id',
            'location_id',
            'properties',
            'properties_detail',
            'remarks',
            'selec_url',
            'last_shared_property_ids',
        ]
    
    def ghl_update(self, instance: Contact):
        urlfield = CustomField.objects.get(field_key='contact.app_preview_url',location_id=instance.location_id)
        remarkfield = CustomField.objects.get(field_key='contact.app_remarks',location_id=instance.location_id)
        payload={
            "customFields": [
                {
                "id": urlfield.id,
                "field_value": instance.selec_url
                },
                {
                "id":remarkfield.id,
                "field_value": instance.remarks
                }
            ],
        }
        ContactServices.push_contact(instance, data=payload)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['properties'] = list(instance.properties.values_list('id', flat=True))
        detail = rep.get('properties_detail') or []
        last_ids = instance.last_shared_property_ids or []
        if not detail or not last_ids:
            return rep

        def norm_key(k):
            if k is None:
                return None
            if isinstance(k, int):
                return k
            try:
                return int(k)
            except (TypeError, ValueError):
                return k

        id_to_item = {item['id']: item for item in detail}
        ordered = []
        seen = set()
        for lid in last_ids:
            key = norm_key(lid)
            cand = id_to_item.get(key) if key is not None else None
            if cand is None:
                cand = id_to_item.get(lid)
            if cand and cand['id'] not in seen:
                ordered.append(cand)
                seen.add(cand['id'])
        for item in detail:
            if item['id'] not in seen:
                ordered.append(item)
                seen.add(item['id'])
        rep['properties_detail'] = ordered
        return rep

    def update(self, instance, validated_data):
        allowed_fields = {'properties', 'remarks', 'selec_url'}
        input_fields = set(validated_data.keys())

        if not input_fields.issubset(allowed_fields):
            raise serializers.ValidationError("Only properties, remarks, and selec_url can be updated.")

        properties = validated_data.pop('properties', None)
        obj = super().update(instance, validated_data)
        if properties is not None:
            if len(properties) == 0:
                raise serializers.ValidationError(
                    {"properties": "Select at least one property to share."}
                )
            ids_this_send = [p.pk for p in properties]
            for p in properties:
                obj.properties.add(p)
            obj.last_shared_property_ids = ids_this_send
            obj.save(update_fields=['last_shared_property_ids'])
        self.ghl_update(obj)
        return obj

        
class XMLFeedSourceSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(required=False)
    subaccounts = serializers.PrimaryKeyRelatedField(
        queryset=OAuthToken.objects.all(),  # replace with your actual model
        many=True,
        required=False  # <-- make it optional
    )

    class Meta:
        model = XMLFeedLink
        fields = [
            "id",
            "url",
            "active",
            "created_at",
            "updated_at",
            "subaccounts",
            "contact_name",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        subaccounts = validated_data.pop('subaccounts', [])
        validated_data["active"] = True
        xml_feed = super().create(validated_data)
        if subaccounts:
            xml_feed.subaccounts.set(subaccounts)

        handle_refresh_xmlfeed_each.delay(xml_feed.url)
        return xml_feed

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['subaccounts'] = LocationSerializer(instance.subaccounts.all(), many=True).data
        return rep

    def validate_url(self, value):
        try:
            response = requests.get(value)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            if not root.findall(".//property"):
                raise serializers.ValidationError(
                    "The provided URL does not contain any <property> elements."
                )
        except (requests.RequestException, ET.ParseError) as e:
            raise serializers.ValidationError(
                f"Invalid or inaccessible XML feed URL: {str(e)}"
            )
        return value

    

class PropertyDataSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='xml_url.contact_name', read_only=True)

    class Meta:
        model = PropertyData
        fields = '__all__'


class XMLFeedSubaccountUpdateSerializer(serializers.ModelSerializer):
    subaccounts = serializers.PrimaryKeyRelatedField(
        many=True, queryset=OAuthToken.objects.all()
    )

    class Meta:
        model = XMLFeedLink
        fields = ['id', 'subaccounts']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['subaccounts'] = LocationSerializer(instance.subaccounts.all(), many=True).data
        return rep