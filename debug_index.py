import json
from pathlib import Path
from collections import defaultdict

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)["Rows"]

pak_path = Path("pak_files")
items_static = load_json(pak_path / "Items/D_ItemsStatic.json")
recipes = load_json(pak_path / "Crafting/D_ProcessorRecipes.json")

# Mapping from D_ItemsStatic
consumable_to_item = {}
for row in items_static:
    item_name = str(row.get("Name", ""))
    consumable_trait = row.get("Consumable", {}).get("RowName", "None")
    if consumable_trait != "None":
        consumable_to_item[consumable_trait] = item_name

print(f"Total mappings in items_static: {len(consumable_to_item)}")
print(f"Mapping for Jam_Jar: {consumable_to_item.get('Jam_Jar')}")

# Indexing recipes
index = defaultdict(list)
for row in recipes:
    recipe_name = str(row.get("Name", ""))
    index[recipe_name].append(row)
    for output in row.get("Outputs", []):
        out_name = str(output.get("Element", {}).get("RowName", ""))
        if out_name:
            index[out_name].append(row)
            for trait_id, itm_id in consumable_to_item.items():
                if itm_id == out_name:
                    index[trait_id].append(row)

print(f"Recipes for Jam_Jar: {len(index.get('Jam_Jar', []))}")
print(f"Recipes for Glass_Jar_Jam: {len(index.get('Glass_Jar_Jam', []))}")

# Check Cooked Prime Meat
print(f"Mapping for Cooked_Prime_Meat: {consumable_to_item.get('Cooked_Prime_Meat')}")
print(f"Recipes for Cooked_Prime_Meat: {len(index.get('Cooked_Prime_Meat', []))}")
