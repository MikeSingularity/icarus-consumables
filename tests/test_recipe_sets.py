import json
import re

def test_recipe_sets():
    # Load consumable data
    with open('pak_files/Traits/D_Consumable.json', 'r', encoding='utf-8') as f:
        consumable_data = json.load(f)
    
    # Load crafting recipes
    with open('pak_files/Crafting/D_ProcessorRecipes.json', 'r', encoding='utf-8') as f:
        recipe_data = json.load(f)
    
    # Create recipe map
    recipe_map = {}
    for row in recipe_data['Rows']:
        recipe_name = row['Name']
        if any(keyword in recipe_name.lower() for keyword in ['food', 'drink', 'beer', 'wine', 'soup', 'stew', 'pie', 'bread', 'cake', 'cookie', 'jam']):
            inputs = []
            if 'Inputs' in row:
                for input_item in row['Inputs']:
                    item_name = input_item['Element']['RowName']
                    count = input_item['Count']
                    inputs.append(f"{item_name} (x{count})")
            
            recipe_sets = []
            if 'RecipeSets' in row:
                for set_info in row['RecipeSets']:
                    recipe_sets.append(set_info['RowName'])
            
            output_name = ""
            if 'Outputs' in row and row['Outputs']:
                output_name = row['Outputs'][0]['Element']['RowName']
            
            recipe_map[output_name] = {
                'inputs': inputs,
                'recipe_sets': recipe_sets,
                'output': output_name
            }
            
            if recipe_name not in recipe_map:
                recipe_map[recipe_name] = {
                    'inputs': inputs,
                    'recipe_sets': recipe_sets,
                    'output': output_name
                }
    
    # Check recipe sets for specific items
    test_items = ["Bread", "FlatBread", "Beer", "Wine", "Dough_Bread"]
    
    print("Recipe sets for test items:")
    print("-" * 50)
    
    for item in test_items:
        found = False
        for recipe_name, recipe in recipe_map.items():
            if (item in recipe_name or 
                recipe_name in item or 
                (recipe['output'] and item in recipe['output']) or 
                (recipe['output'] and recipe['output'] in item)):
                print(f"Item '{item}'")
                print(f"  Recipe: '{recipe_name}'")
                print(f"  Recipe Sets: {recipe['recipe_sets']}")
                print()
                found = True
                break
        
        if not found:
            print(f"No recipe found for item '{item}'")
            print()
    
    # Print some items with recipes
    print("Items with recipes (first 20):")
    print("-" * 50)
    count = 0
    for item in consumable_data['Rows']:
        if item['Name'] in ["BasicFood", "AdvancedFood", "Meta_Bolt_Set_Larkwell_Piercing"]:
            continue
        
        item_name = item['Name']
        found = False
        
        for recipe_name, recipe in recipe_map.items():
            if (item_name in recipe_name or 
                recipe_name in item_name or 
                (recipe['output'] and item_name in recipe['output']) or 
                (recipe['output'] and recipe['output'] in item_name)):
                print(f"Item '{item_name}'")
                print(f"  Recipe: '{recipe_name}'")
                print(f"  Recipe Sets: {recipe['recipe_sets']}")
                print()
                found = True
                count += 1
                if count >= 20:
                    return
        
        if found:
            continue

if __name__ == "__main__":
    test_recipe_sets()