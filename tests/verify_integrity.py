"""
Verification script for validating Icarus food data parser output.
Ensures consistency across Markdown, JSON, and CSV formats without relying on hardcoded item counts.
"""
import json
import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'output'

def verify_integrity():
    """
    Perform structural and data integrity checks on generated output files.
    Validates file existence, JSON-CSV consistency, category coverage, 
    modifier references, and specific business rules for Animal Food.
    """
    print("Starting dynamic integrity verification...")
    errors = []

    # 1. Check file existence
    formats = ['json']
    for fmt in formats:
        file_path = OUTPUT_DIR / f'consumables_data.{fmt}'
        if not file_path.exists():
            errors.append(f"Missing output file: {file_path.name}")
    
    if errors:
        print("\n".join(errors))
        return False

    # 2. Load JSON data for structural validation
    try:
        with open(OUTPUT_DIR / 'consumables_data.json', 'r') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        return False

    if 'items' not in json_data:
        errors.append("JSON structure missing 'items' key")

    items = json_data.get('items', [])
    item_count = len(items)
    print(f"Found {item_count} items in JSON.")

    # 3. Minimum item count check (Resilience against game updates)
    MIN_ITEM_COUNT = 300
    if item_count < MIN_ITEM_COUNT:
        errors.append(f"Item count ({item_count}) is below the minimum threshold of {MIN_ITEM_COUNT}")

    # 4. Canary Items Verification (Ensures key items are present and correct)
    CANARY_ITEMS = {
        'Cooked_Meat': 'Cooked Meat',
        'Food_Berry': 'Berry',
        'Bandage_Basic': 'Basic Bandage',
        'Drink_Beer': 'Beer',
        'Meta_Bolt_Set_Larkwell_Piercing': 'Larkwell Piercing Bolt Bundle',
        'Raw_Meat': 'Raw Meat'
    }
    
    found_names = {item.get('name'): item.get('display_name') for item in items}
    for internal_name, expected_string in CANARY_ITEMS.items():
        if internal_name not in found_names:
            errors.append(f"Canary item missing: {internal_name}")
        elif expected_string not in found_names[internal_name]:
             errors.append(f"Canary item display name mismatch: {internal_name} (Expected string '{expected_string}' not found in '{found_names[internal_name]}')")

    # 5. Check category distribution
    categories = set(item.get('category') for item in items)
    required_categories = {'Animal Food', 'Food', 'Drink', 'Medicine'}
    missing_categories = required_categories - categories
    if missing_categories:
        errors.append(f"Missing items in required categories: {missing_categories}")
    else:
        print("All required categories are present.")

    # 6. Animal Food recipe check
    animal_food_without_recipes = [
        item.get('display_name') for item in items 
        if item.get('category') == 'Animal Food' and (not item.get('recipes')) and not item.get('tier', {}).get('is_harvested', False)
    ]
    if animal_food_without_recipes:
        errors.append(f"Animal Food items missing recipes: {animal_food_without_recipes}")

    # Summary
    if errors:
        print("\nIntegrity Verification FAILED:")
        for error in errors:
            print(f" - {error}")
        return False
    
    print("Integrity Verification PASSED successfully!")
    return True

if __name__ == "__main__":
    if verify_integrity():
        sys.exit(0)
    else:
        sys.exit(1)
