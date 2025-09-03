from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.db import models
import re

# Import your Contact model - replace 'your_app' with actual app name
from core.models import Contact

def clean_price_value(price_str):
    """Convert price string with k/m notation to actual number"""
    if not price_str:
        return None
    
    original_value = price_str
    price_str = str(price_str).lower().strip()
    
    # Check for millions (m)
    if price_str.endswith('m'):
        numeric_part = price_str[:-1]
        try:
            base_value = Decimal(numeric_part)
            converted = str(int(base_value * 1000000))
            print(f"  {original_value} -> {converted}")
            return converted
        except (InvalidOperation, ValueError):
            print(f"  Failed to convert: {original_value}")
            return None
    
    # Check for thousands (k)
    elif price_str.endswith('k'):
        numeric_part = price_str[:-1]
        try:
            base_value = Decimal(numeric_part)
            converted = str(int(base_value * 1000))
            print(f"  {original_value} -> {converted}")
            return converted
        except (InvalidOperation, ValueError):
            print(f"  Failed to convert: {original_value}")
            return None
    
    return None  # No conversion needed

def update_contact_prices(dry_run=True):
    """
    Update all contacts with k/m notation in price fields
    
    Args:
        dry_run (bool): If True, only show what would be updated without making changes
    """
    
    if dry_run:
        print("=== DRY RUN MODE - No changes will be made ===\n")
    
    # Find contacts with k or m in price fields
    contacts_with_km_prices = Contact.objects.filter(
        models.Q(min_price__iregex=r'.*[km]$') |  # ends with k or m
        models.Q(max_price__iregex=r'.*[km]$')
    )
    
    total_contacts = contacts_with_km_prices.count()
    print(f"Found {total_contacts} contacts with k/m notation in price fields\n")
    
    if total_contacts == 0:
        print("No contacts need updating!")
        return
    
    updated_count = 0
    error_count = 0
    
    # Show first few examples
    print("Examples of what will be updated:")
    for contact in contacts_with_km_prices[:5]:
        print(f"Contact {contact.id}:")
        if contact.min_price:
            print(f"  min_price: {contact.min_price}")
        if contact.max_price:
            print(f"  max_price: {contact.max_price}")
        print()
    
    if dry_run:
        proceed = input(f"Proceed with dry run of all {total_contacts} contacts? (y/N): ")
    else:
        proceed = input(f"Proceed with updating all {total_contacts} contacts? This will modify your database! (y/N): ")
    
    if proceed.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Process all contacts
    with transaction.atomic():
        for contact in contacts_with_km_prices:
            print(f"\nProcessing contact {contact.id}:")
            
            updates = {}
            
            # Process min_price
            if contact.min_price and contact.min_price.lower().endswith(('k', 'm')):
                new_min_price = clean_price_value(contact.min_price)
                if new_min_price is not None:
                    updates['min_price'] = new_min_price
            
            # Process max_price
            if contact.max_price and contact.max_price.lower().endswith(('k', 'm')):
                new_max_price = clean_price_value(contact.max_price)
                if new_max_price is not None:
                    updates['max_price'] = new_max_price
            
            # Update the contact if we have changes
            if updates:
                if not dry_run:
                    try:
                        Contact.objects.filter(id=contact.id).update(**updates)
                        updated_count += 1
                        print(f"  ✓ Updated contact {contact.id}")
                    except Exception as e:
                        error_count += 1
                        print(f"  ✗ Error updating {contact.id}: {e}")
                else:
                    updated_count += 1
                    print(f"  ✓ Would update contact {contact.id}")
    
    # Summary
    print("\n" + "="*50)
    if dry_run:
        print(f"DRY RUN COMPLETE: Would update {updated_count} contacts")
    else:
        print(f"Successfully updated {updated_count} contacts")
    
    if error_count > 0:
        print(f"Errors encountered: {error_count}")

# Usage examples:
# 1. First run with dry_run=True to see what would be changed:
# update_contact_prices(dry_run=True)

# 2. Then run with dry_run=False to actually update:
# update_contact_prices(dry_run=False)

print("To use this script:")
print("1. First run: update_contact_prices(dry_run=True)")
print("2. Then run: update_contact_prices(dry_run=False)")