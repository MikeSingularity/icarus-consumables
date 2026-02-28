import csv
from typing import List
from icarus_food.generators.base import BaseGenerator
from icarus_food.models.consumable import ConsumableData

class CsvGenerator(BaseGenerator):
    """Generates CSV output for spreadsheet applications."""

    def generate(self, data: List[ConsumableData]) -> None:
        # 1. Collect all unique modifier effect keys
        all_effect_keys = set()
        for item in data:
            for mod in item.modifiers:
                all_effect_keys.update(mod.effects.keys())
        
        sorted_effect_keys = sorted(list(all_effect_keys))

        # 2. Define headers
        headers = [
            "Category", "Item Name", "Food", "Water", "Health", "Oxygen"
        ] + sorted_effect_keys + [
            "Modifier", "Duration (seconds)", "Ingredients", 
            "Crafting Bench", "Tier", "Requirements"
        ]
        
        with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            # Sort by category then tier
            categories = ["Animal Food", "Food", "Drink", "Medicine"]
            sorted_data = sorted(data, key=lambda x: (
                categories.index(x.category) if x.category in categories else 99, 
                x.tier_info.total_tier
            ))
            
            for item in sorted_data:
                stats = item.base_stats
                
                # Modifier Info
                mod_name = ""
                duration = ""
                effect_values = {key: "" for key in sorted_effect_keys}
                if item.modifiers:
                    mod = item.modifiers[0]
                    mod_name = mod.display_name
                    duration = mod.lifetime
                    for key, val in mod.effects.items():
                        effect_values[key] = val

                # Recipe Info
                ingredients = ""
                bench = ""
                reqs = ""
                if item.recipes:
                    recipe = item.recipes[0]
                    ingredients = ", ".join([f"{ing.count}x {ing.item.display_name}" for ing in recipe.inputs])
                    bench = ", ".join(recipe.benches)
                    all_reqs = []
                    if recipe.requirement and recipe.requirement != "None":
                        all_reqs.append(f"Talent: {recipe.requirement}")
                    if recipe.character_req:
                        all_reqs.append(f"Flag: {recipe.character_req}")
                    if recipe.session_req:
                        all_reqs.append(f"Session: {recipe.session_req}")
                    reqs = "; ".join(all_reqs)

                # Build row with numeric types where possible
                row = [
                    item.category,
                    item.display_name,
                    stats.get("Food", ""),
                    stats.get("Water", ""),
                    stats.get("Health", ""),
                    stats.get("Oxygen", "")
                ]
                # Add individual modifier effect values
                for key in sorted_effect_keys:
                    row.append(effect_values[key])
                
                # Add remaining columns
                row.extend([
                    mod_name,
                    duration,
                    ingredients,
                    bench,
                    item.tier_info.total_tier if not item.tier_info.is_harvested else 0,
                    reqs
                ])
                writer.writerow(row)
