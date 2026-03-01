from icarus_consumables.services.translation import IcarusTranslationService
from icarus_consumables.services.recipe_service import RecipeService
from icarus_consumables.services.tier_mapper import IcarusTierMapper
from icarus_consumables.services.modifier_service import ModifierService
from icarus_consumables.services.category_service import CategoryService
from icarus_consumables.services.override_service import OverrideService
from icarus_consumables.services.farming_service import FarmingService
from icarus_consumables.models.consumable import ConsumableData
import re
from typing import Any, Optional, List, Set, Dict

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
        farming_service: FarmingService,
        item_index_service: Any,
        decayable_rows: list[dict[str, Any]] = None
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
        self.item_index_service = item_index_service
        self.decayable_rows = decayable_rows or []

    def parse_all(self, consumable_rows: list[dict[str, Any]], itemable_rows: list[dict[str, Any]], items_static: list[dict[str, Any]], decayable_rows: list[dict[str, Any]] = None) -> list[ConsumableData]:
        """
        Parses all consumable rows into a list of ConsumableData objects.
        """
        decayable_rows = decayable_rows or self.decayable_rows
        decay_products = set()
        for row in decayable_rows:
            spoiled = row.get("SpoiledItem", {}).get("RowName")
            if spoiled and spoiled != "None":
                decay_products.add(spoiled)

        # Build a map from consumable piece name to its parent item name (e.g., Chocolate_Cake_Piece -> Chocolate_Cake)
        parent_item_map = {}
        auto_suppressed = set()
        for row in items_static:
            name = str(row.get("Name"))
            
            # Identify parent/child relationships (e.g., Chocolate_Cake -> Chocolate_Cake_Piece)
            # Only map if the child name contains the parent name to prevent generic trait sharing (Raw_Meat)
            child_name = row.get("Consumable", {}).get("RowName")
            if child_name and child_name != "None" and child_name != name:
                # Heuristic: Child name should structurally contain the parent name
                # This prevents "Raw_Chicken" being the parent of "Raw_Meat"
                if name.lower() in child_name.lower():
                    parent_item_map[child_name] = name
            
            # Identify reusable equipment (Fillable containers like Canteens, Oxygen Tanks)
            if "Fillable" in row and row.get("Fillable", {}).get("RowName", "") != "None":
                auto_suppressed.add(name)
                # Also suppress the specific consumable RowName if it is different
                if child_name and child_name != "None":
                    auto_suppressed.add(child_name)
                    
            # Identify items explicitly blacklisted from the Field Guide (transient/internal items)
            tags = [t.get("TagName") for t in row.get("Manual_Tags", {}).get("GameplayTags", [])] + \
                   [t.get("TagName") for t in row.get("Generated_Tags", {}).get("GameplayTags", [])]
            
            # AUTOMATED VISIBILITY: Identify items that carry the Consumable tag
            # This ensures items like Raw_Bacon (which shares Raw_Meat trait) are visible
            if any(t.startswith("Item.Consumable") for t in tags):
                # We don't necessarily show everything, but we ensure it's not hidden
                # unless explicitly blacklisted
                pass
            else:
                # If it's not a consumable tag and not in D_Consumable, it might be internal
                # This logic will be applied in parse_all to items not in processed_names
                pass

            if "FieldGuide.BlackList" in tags:
                auto_suppressed.add(name)
                if child_name and child_name != "None":
                    auto_suppressed.add(child_name)

        results = []
        processed_names = set()

        for row in consumable_rows:
            name = str(row.get("Name"))
            
            # Safe heuristic for deduplication: Ask the index if this consumable ID ("Food_Berry") 
            # is just the D_Consumable half of an item that is natively represented in D_ItemsStatic ("Berry" or "Item_Berry").
            # If so, we skip the raw consumable loop here because the items_static loop at the bottom 
            # will catch it, process it, and have the full contextual tag/tier data.
            static_equiv = self.item_index_service.translate_id("D_Consumable", "D_ItemsStatic", name)
            if static_equiv and static_equiv != "None":
                # Only skip if the static equivalent isn't literally just itself
                if static_equiv != name:
                    # Verify the static equivalent actually exists in our D_ItemsStatic JSON dump
                    # (Some links exist in the index but represent deprecated items)
                    if any(str(i.get("Name")) == static_equiv for i in items_static):
                        # But we MUST add it to processed_names so it doesn't get double-processed 
                        # as a raw "not in items_static but has Consumable tag" item later down the chain
                        processed_names.add(name)
                        continue
            
            processed_names.add(name)
            
            consumable = self._parse_row(row, itemable_rows, items_static, parent_item_map, auto_suppressed, decay_products)
            # Only include visible items in the final output
            if consumable and consumable.is_visible:
                results.append(consumable)

        # Handle items that might only exist in ItemsStatic but link here
        for child_name, parent_name in parent_item_map.items():
            if child_name not in processed_names:
                # Create a placeholder row
                placeholder_row = {"Name": child_name}
                consumable = self._parse_row(placeholder_row, itemable_rows, items_static, parent_item_map, auto_suppressed, decay_products)
                if consumable and consumable.is_visible:
                    results.append(consumable)

        # Add items from Item.Consumable tags that weren't in D_Consumable
        for row in items_static:
            name = str(row.get("Name"))
            if name in processed_names: continue
            
            tags = [t.get("TagName") for t in row.get("Manual_Tags", {}).get("GameplayTags", [])] + \
                   [t.get("TagName") for t in row.get("Generated_Tags", {}).get("GameplayTags", [])]
            
            if any(t.startswith("Item.Consumable") for t in tags):
                # We need to process this static item. 
                
                # Step 1: Check for generic trait inheritance (e.g., Raw_Food)
                trait_id = row.get("Consumable", {}).get("RowName", "None")
                target_row = {"Name": name, "Stats": {}, "Modifier": {}} 
                
                if trait_id and trait_id != "None":
                    trait_row = next((c for c in consumable_rows if str(c.get("Name")) == trait_id), None)
                    if trait_row:
                        # Use trait as base, but preserve item's original name
                        target_row = trait_row.copy()
                        target_row["Name"] = name
                
                # Step 2: Check for specific consumable counterpart (e.g. Kumara -> Food_Kumara)
                # This should override the generic trait if it exists
                consumable_id = self.item_index_service.translate_id("D_ItemsStatic", "D_Consumable", name)
                
                if consumable_id and consumable_id != "None" and consumable_id != trait_id:
                    spec_row = next((c for c in consumable_rows if str(c.get("Name")) == consumable_id), None)
                    if spec_row:
                        # Overwrite base trait stats/modifiers with specific ones
                        target_row.update(spec_row)
                        target_row["Name"] = name # Ensure name remains item-specific
                
                consumable = self._parse_row(target_row, itemable_rows, items_static, parent_item_map, auto_suppressed, decay_products)
                if consumable and consumable.is_visible:
                    results.append(consumable)

        # Add items from overrides that weren't in the game data
        for name in self.override_service.get_all_overridden_items():
            if name not in results and name not in processed_names:
                # Create a placeholder row
                placeholder_row = {"Name": name, "Stats": {}, "Modifier": {}}
                consumable = self._parse_row(placeholder_row, itemable_rows, items_static, parent_item_map, auto_suppressed, decay_products)
                if consumable and consumable.is_visible:
                    results.append(consumable)

        return results

    def _parse_row(self, row: dict[str, Any], itemable_rows: list[dict[str, Any]], items_static: list[dict[str, Any]], parent_item_map: dict[str, str], auto_suppressed: set[str], decay_products: set[str]) -> Optional[ConsumableData]:
        """
        Parses a single row from D_Consumable into a ConsumableData object.
        """
        name = str(row.get("Name"))
        
        # Determine normalized ID and source tracking
        norm_id = self.item_index_service.get_normalized_id("D_Consumable", name)
        if not norm_id: # For placeholders or ItemsStatic Fallbacks
            norm_id = self.item_index_service.get_normalized_id("D_ItemsStatic", name)
        if not norm_id:
            norm_id = self.item_index_service._normalize_id(name)
            
        source_ids = self.item_index_service.norm_to_source.get(norm_id, {}).copy()
        if not source_ids:
            # If it was an override or something totally unindexed
            source_ids = {"Unknown": name}
        
        # 1. Basic Metadata
        display_name = self.translation.get_display_name(name)
        description = self.translation.get_description(name, itemable_rows)
        
        consumable = ConsumableData(
            name=norm_id,
            display_name=display_name,
            description=description
        )
        consumable.source_ids = source_ids
        
        # Identify Decay Products
        if name in decay_products or row.get("Name") in decay_products:
            consumable.is_decay_product = True
        
        # Populate Yield Information (Trait-based)
        yield_info = self.translation.get_yield_info(name)
        if yield_info:
            target_yield, count = yield_info
            # SUPPRESS: If this item has explicit recipes on a Butchery/Skinning bench,
            # we favor that over the automated trait-based yield link.
            # This prevents Bacon -> Raw_Meat "yields" links when there is a recipe.
            has_explicit_recipes = False
            rows = self.recipe_service.get_recipe_rows_for_item(name)
            for r in rows:
                benches = [b.get("RowName") for b in r.get("RecipeSets", [])]
                if any(b in ["Skinning_Bench", "Butchery_Bench", "Advanced_Butchery_Bench"] for b in benches):
                    has_explicit_recipes = True
                    break
            
            if not has_explicit_recipes:
                yield_norm = self.item_index_service.get_normalized_id("D_ItemsStatic", target_yield)
                if not yield_norm:
                    yield_norm = self.item_index_service._normalize_id(target_yield)
                consumable.yields_item, consumable.yields_count = yield_norm, count

        # Apply Automated Visibility Suppression (Reusable equipment, Blacklisted items)
        if name in auto_suppressed:
            consumable.is_visible = False

        # 2. Base Stats
        stats = self._parse_stats(row.get("Stats", {}))
        consumable.base_stats = stats
        
        parent_name = parent_item_map.get(name)
        if parent_name:
            parent_norm = self.item_index_service.get_normalized_id("D_ItemsStatic", parent_name)
            if not parent_norm:
                parent_norm = self.item_index_service._normalize_id(parent_name)
            consumable.source_item = parent_norm
        
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
                    if ing.item:
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

        # 9. Refined Aggressive Suppression (Food category junk data)
        # Suppress "Food" that has no recipes and no "true" core traits (harvested, orbital, decay)
        if consumable.is_visible and consumable.category == "Food":
            has_recipes = len(consumable.recipes) > 0
            has_core_traits = (
                consumable.tier_info.is_harvested or 
                consumable.tier_info.is_orbital or 
                consumable.is_decay_product
            )
            if not has_recipes and not has_core_traits:
                consumable.is_visible = False

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
