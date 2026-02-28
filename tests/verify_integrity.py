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
    formats = ['md', 'json', 'csv', 'ods']
    for fmt in formats:
        file_path = OUTPUT_DIR / f'icarus_food_guide.{fmt}'
        if not file_path.exists():
            errors.append(f"Missing output file: {file_path.name}")
    
    if errors:
        print("\n".join(errors))
        return False

    # 2. Load JSON data for structural validation
    try:
        with open(OUTPUT_DIR / 'icarus_food_guide.json', 'r') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        return False

    if 'Items' not in json_data or 'Modifiers' not in json_data:
        errors.append("JSON structure missing 'Items' or 'Modifiers' keys")

    items = json_data.get('Items', [])
    modifiers = json_data.get('Modifiers', {})

    print(f"Found {len(items)} items and {len(modifiers)} unique modifiers in JSON.")

    # 3. Verify CSV consistency
    try:
        with open(OUTPUT_DIR / 'icarus_food_guide.csv', 'r') as f:
            csv_reader = csv.reader(f)
            csv_rows = list(csv_reader)
            # Row count should be items + 1 (header)
            if len(csv_rows) != len(items) + 1:
                errors.append(f"CSV row count ({len(csv_rows)}) does not match JSON item count ({len(items)}) + 1")
    except Exception as e:
        errors.append(f"Failed to verify CSV: {e}")

    # 4. Check category distribution
    categories = set(item.get('Category') for item in items)
    required_categories = {'Animal Food', 'Food', 'Drink', 'Medicine'}
    missing_categories = required_categories - categories
    if missing_categories:
        errors.append(f"Missing items in required categories: {missing_categories}")
    else:
        print("All required categories are present.")

    # 5. Verify modifier references
    for item in items:
        mod_name = item.get('Modifier')
        if mod_name and mod_name not in modifiers:
            errors.append(f"Item '{item.get('Item Name')}' references unknown modifier '{mod_name}'")

    # 6. Animal Food recipe check (from CLAUDE.md: "All Animal Food items have recipes")
    animal_food_without_recipes = [
        item.get('Item Name') for item in items 
        if item.get('Category') == 'Animal Food' and (not item.get('Ingredients') or item.get('Tier') == 0)
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
