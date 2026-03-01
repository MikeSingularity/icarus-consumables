from typing import List
from icarus_consumables.generators.base import BaseGenerator
from icarus_consumables.models.consumable import ConsumableData

try:
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
    HAS_ODF = True
except ImportError:
    HAS_ODF = False

class OdsGenerator(BaseGenerator):
    """Generates a true ODS file using the odfpy library for LibreOffice compatibility."""

    def generate(self, data: List[ConsumableData]) -> None:
        if not HAS_ODF:
            print("⚠️ Skipping ODS generation: 'odfpy' library not installed.")
            return

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

        doc = OpenDocumentSpreadsheet()
        table = Table(name="Icarus Food Guide")

        # Write headers
        header_row = TableRow()
        for header in headers:
            cell = TableCell()
            cell.addElement(P(text=header))
            header_row.addElement(cell)
        table.addElement(header_row)

        # Sort by category then tier
        categories = ["Animal Food", "Food", "Drink", "Medicine"]
        sorted_data = sorted(data, key=lambda x: (
            categories.index(x.category) if x.category in categories else 99, 
            x.tier_info.total_tier
        ))

        # Write data
        for item in sorted_data:
            stats = item.base_stats
            
            # Modifier Info
            mod_name = ""
            duration = None
            effect_values = {key: None for key in sorted_effect_keys}
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

            # Build row values
            row_values = [
                item.category,
                item.display_name,
                stats.get("Food"),
                stats.get("Water"),
                stats.get("Health"),
                stats.get("Oxygen")
            ]
            for key in sorted_effect_keys:
                row_values.append(effect_values[key])
            
            row_values.extend([
                mod_name,
                duration,
                ingredients,
                bench,
                item.tier_info.total_tier if not item.tier_info.is_harvested else 0,
                reqs
            ])

            row = TableRow()
            for value in row_values:
                cell = TableCell()
                if value is not None and value != "":
                    # Determine value type for ODS
                    if isinstance(value, (int, float)):
                        cell.setAttribute('valuetype', 'float')
                        cell.setAttribute('value', str(value))
                        cell.addElement(P(text=str(value)))
                    else:
                        cell.setAttribute('valuetype', 'string')
                        cell.addElement(P(text=str(value)))
                row.addElement(cell)
            table.addElement(row)

        doc.spreadsheet.addElement(table)
        doc.save(str(self.output_path))
