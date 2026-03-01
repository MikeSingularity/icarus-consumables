from typing import List
from icarus_consumables.generators.base import BaseGenerator
from icarus_consumables.models.consumable import ConsumableData

class MarkdownGenerator(BaseGenerator):
    """Generates a human-readable Markdown guide."""

    def generate(self, data: List[ConsumableData]) -> None:
        content = ["# Icarus Food and Drinks Guide\n"]
        
        categories = ["Animal Food", "Food", "Drink", "Medicine"]
        for cat in categories:
            cat_items = [i for i in data if i.category == cat]
            if not cat_items:
                continue
                
            content.append(f"## {cat}\n")
            content.append("| Item | Effects | Modifier | Duration | Ingredients | Bench | Tier | Requirements |")
            content.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            
            for item in sorted(cat_items, key=lambda x: x.tier_info.total_tier):
                effects = self._format_stats(item)
                
                # Modifier
                mod_name = "-"
                mod_effects = "-"
                duration = "-"
                if item.modifiers:
                    mod = item.modifiers[0]
                    mod_name = mod.display_name
                    duration = f"{mod.lifetime}s"
                    mod_effects = ", ".join([f"{k}: {v:+g}" for k, v in mod.effects.items()])

                # Recipe
                ingredients = "-"
                bench = "-"
                reqs = "-"
                if item.recipes:
                    recipe = item.recipes[0] # Take first for display
                    ingredients = ", ".join([f"{ing.count}x {ing.item.display_name}" for ing in recipe.inputs])
                    bench = ", ".join(recipe.benches)
                    
                    # Combine requirements
                    all_reqs = []
                    if recipe.requirement and recipe.requirement != "None":
                        all_reqs.append(f"Talent: {recipe.requirement}")
                    if recipe.character_req:
                        all_reqs.append(f"Flag: {recipe.character_req}")
                    if recipe.session_req:
                        all_reqs.append(f"Session: {recipe.session_req}")
                    reqs = "; ".join(all_reqs) if all_reqs else "-"

                tier_display = f"{item.tier_info.total_tier:.1f}" if not item.tier_info.is_harvested else "0"

                row = f"| {item.display_name} | {effects} | {mod_name} ({mod_effects}) | {duration} | {ingredients} | {bench} | {tier_display} | {reqs} |"
                content.append(row)
            content.append("\n")

        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
