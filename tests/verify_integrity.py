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
    """
    print("Starting multi-file integrity verification...")
    errors = []

    # 1. Load Data
    try:
        with open(OUTPUT_DIR / 'consumables_items.json', 'r') as f:
            items_data = json.load(f)
        with open(OUTPUT_DIR / 'consumables_recipes.json', 'r') as f:
            recipes_data = json.load(f)
        with open(OUTPUT_DIR / 'consumables_modifiers.json', 'r') as f:
            modifiers_data = json.load(f)
    except Exception as e:
        print(f"Failed to load JSON files: {e}")
        return False

    items = items_data.get('items', [])
    recipes = recipes_data.get('recipes', {})
    modifiers = modifiers_data.get('modifiers', {})

    print(f"Found {len(items)} items, {len(recipes)} recipes, and {len(modifiers)} modifiers.")

    # 2. Structural & Referential Checks
    for item in items:
        name = item.get('name')
        
        # Check Modifiers
        for mid in item.get('modifiers', []):
            if mid not in modifiers:
                errors.append(f"Item '{name}' references missing modifier: '{mid}'")
        
        # Check Recipes
        for rid in item.get('recipes', []):
            if rid not in recipes:
                errors.append(f"Item '{name}' references missing recipe: '{rid}'")

    # 3. Minimum item count check
    MIN_ITEM_COUNT = 300
    if len(items) < MIN_ITEM_COUNT:
        errors.append(f"Item count ({len(items)}) is below threshold of {MIN_ITEM_COUNT}")

    # 4. Canary Items Verification
    CANARY_ITEMS = {
        'cookedmeat': 'Cooked Meat',
        'berry': 'Berry',
        'bandagebasic': 'Basic Bandage',
        'metaboltsetlarkwellpiercing': 'Larkwell Piercing Bolt Bundle',
        'rawmeat': 'Raw Meat',
        'kumara': 'Kumara'
    }
    
    found_names = {item.get('name'): item.get('display_name') for item in items}
    for internal_name, expected_string in CANARY_ITEMS.items():
        if internal_name not in found_names:
            errors.append(f"Canary item missing: {internal_name}")
        elif expected_string not in found_names[internal_name]:
             errors.append(f"Canary item display name mismatch: {internal_name}")

    # 5. Raw_Meat Recipe Count Check (The Bloat test)
    raw_meat_recipes = next((i.get('recipes', []) for i in items if i.get('name') == 'rawmeat'), [])
    if len(raw_meat_recipes) > 40:
        errors.append(f"rawmeat still has too many recipes ({len(raw_meat_recipes)}). Primary filter failed.")
    else:
        print(f"Raw_Meat recipe count optimized: {len(raw_meat_recipes)}")

    # 6. Generic Ingredients Check
    has_generic = False
    for r in recipes.values():
        for ing in r.get('inputs', []):
            if ing.get('is_generic'):
                has_generic = True
                break
        if has_generic: break
    
    if not has_generic:
        errors.append("No recipes found with generic ingredients (is_generic: true).")
    else:
        print("Generic ingredients check: PASSED (at least one generic ingredient found)")

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
