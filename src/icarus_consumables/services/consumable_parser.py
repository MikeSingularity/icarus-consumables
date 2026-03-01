from icarus_consumables.services.translation import IcarusTranslationService
from icarus_consumables.services.recipe_service import RecipeService
from icarus_consumables.services.tier_mapper import IcarusTierMapper
from icarus_consumables.services.modifier_service import ModifierService
from icarus_consumables.services.category_service import CategoryService
from icarus_consumables.services.override_service import OverrideService
from icarus_consumables.services.farming_service import FarmingService
from icarus_consumables.models.consumable import ConsumableData
import re
from typing import Any

class ConsumableDataParser:
    """
    Orchestrates the extraction and assembly of consumable data from game files.
    """

    def __init__(
        self, 
        translation_service: IcarusTranslationService,
        recipe_service: RecipeService,
        tier_mapper: IcarusTierMapper,
        modifier_service: ModifierService,
        category_service: CategoryService,
        override_service: OverrideService,
        farming_service: FarmingService
    ):
        """
        Initializes the parser with its required service dependencies.
        """
        self.translation = translation_service
        self.recipe_service = recipe_service
        self.tier_mapper = tier_mapper
        self.modifier_service = modifier_service
        self.category_service = category_service
        self.override_service = override_service
        self.farming_service = farming_service

    def parse_all(self, consumable_rows: list[dict[str, Any]], itemable_rows: list[dict[str, Any]], items_static: list[dict[str, Any]]) -> list[ConsumableData]:
        """
        Parses all consumable rows into a list of ConsumableData objects.
        """
        # Build a map from consumable piece name to its parent item name (e.g., Chocolate_Cake_Piece -> Chocolate_Cake)
        parent_item_map = {}
        for row in items_static:
            parent_name = str(row.get("Name"))
            child_name = str(row.get("Consumable", {}).get("RowName", ""))
            if child_name and child_name != "None" and child_name != parent_name:
                parent_item_map[child_name] = parent_name

        results = []
        processed_names = set()

        for row in consumable_rows:
            name = str(row.get("Name"))
            processed_names.add(name)
            
            consumable = self._parse_row(row, itemable_rows, items_static, parent_item_map)
            if consumable:
                results.append(consumable)

        # Add items from overrides that weren't in the game data
        for name in self.override_service.get_all_overridden_items():
            if name not in processed_names:
                # Create a placeholder row
                placeholder_row = {"Name": name, "Stats": {}, "Modifier": {}}
                consumable = self._parse_row(placeholder_row, itemable_rows, items_static, parent_item_map)
                if consumable and consumable.is_visible:
                    results.append(consumable)

        return results

    def _parse_row(self, row: dict[str, Any], itemable_rows: list[dict[str, Any]], items_static: list[dict[str, Any]], parent_item_map: dict[str, str]) -> ConsumableData:
        """Parses a single row into ConsumableData."""
        name = str(row.get("Name"))
        
        # 1. Basic Item Data
        display_name = self.translation.get_display_name(name)
        description = self.translation.get_description(name, itemable_rows)

        # 2. Base Stats
        stats = self._parse_stats(row.get("Stats", {}))
        
        # 3. Initial Object Construction
        consumable = ConsumableData(
            name=name,
            display_name=display_name,
            description=description,
            category="", # Will be assigned below
            base_stats=stats,
            source_item=parent_item_map.get(name)
        )
        
        # 4. Modifiers
        mod_data = row.get("Modifier", {})
        mod_id = str(mod_data.get("Modifier", {}).get("RowName"))
        if mod_id and mod_id != "None":
            lifetime = int(mod_data.get("ModifierLifetime", 0))
            modifier = self.modifier_service.get_modifier_effect(mod_id, lifetime)
            if modifier:
                consumable.modifiers.append(modifier)
        
        # 5. Recipes & Tiers
        matched_recipes = self.recipe_service.get_recipes_for_item(name)
        if matched_recipes:
            # Resolve display names for ingredients and benches
            for recipe in matched_recipes:
                for ing in recipe.inputs:
                    ing.item.display_name = self.translation.get_display_name(ing.item.name)
                for res in recipe.outputs:
                    res.item.display_name = self.translation.get_display_name(res.item.name)
                    yield_info = self.translation.get_yield_info(res.item.name)
                    if yield_info:
                        res.item.yields_item, res.item.yields_count = yield_info
                
                translated_benches = []
                for bench in recipe.benches:
                    translated_benches.append(self.translation.get_display_name(bench))
                recipe.benches = translated_benches

            consumable.recipes = matched_recipes
            
            # For tiering, we use the lowest tier among available recipes
            recipe_rows = self.recipe_service.get_recipe_rows_for_item(name)
            best_tier_info = None
            for raw_rec in recipe_rows:
                tier_info = self.tier_mapper.calculate_tier(name, raw_rec)
                if not best_tier_info or tier_info.total_tier < best_tier_info.total_tier:
                    best_tier_info = tier_info
            
            if best_tier_info:
                consumable.tier_info = best_tier_info
        else:
            # Harvested item
            consumable.tier_info = self.tier_mapper.calculate_tier(name, None)

        # 6. Category Assignment
        consumable.category = self.category_service.assign_category(name, stats)

        # 7. Growth Data Extraction
        self._extract_growth_data(consumable, row)

        # 8. Apply Overrides (Last word)
        self.override_service.apply_overrides(name, consumable)

        return consumable

    def _extract_growth_data(self, consumable: ConsumableData, row: dict[str, Any]):
        """
        Extracts growth time and harvest yield if applicable.
        """
        info = self.farming_service.get_growth_info(consumable.name)
        if info:
            consumable.growth_time = info.time_seconds
            consumable.harvest_yield = f"{info.yield_min}-{info.yield_max}"

    def _parse_stats(self, stats_row: dict[str, Any]) -> dict[str, float]:
        """
        Cleans up stat keys and values.
        """
        stats: dict[str, float] = {}
        for key, value in stats_row.items():
            match = re.search(r'Base(.*?)(Recovery)?_.*?"', str(key))
            if match:
                stat_name = match.group(1)
                stats[stat_name] = float(value)
            else:
                stats[str(key)] = float(value)
        return stats

    def _assign_category(self, name: str, stats: dict[str, float]) -> str:
        """
        Assigns item category based on stats and name.
        """
        if "Food" in stats:
            if "Animal" in name or "Omni" in name:
                return "Animal Food"
            return "Food"
        if "Water" in stats:
            return "Drink"
        return "Medicine"
