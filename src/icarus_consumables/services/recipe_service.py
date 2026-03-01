from typing import Any, Optional
from icarus_consumables.models.recipe import Recipe, Ingredient
from icarus_consumables.models.item import IcarusItem

class RecipeService:
    """
    Manages the mapping of crafting recipes to consumable items.
    """

    def __init__(self, recipe_rows: list[dict[str, Any]], items_static: list[dict[str, Any]], tag_service: Any = None):
        """
        Initializes the service and builds a composite index of recipes.
        """
        self.tag_service = tag_service
        self.recipes = recipe_rows
        self.recipe_map = self._build_composite_index(recipe_rows, items_static)
        self.tier_mapper: Optional[Any] = None

    def set_tier_mapper(self, tier_mapper: Any):
        """
        Injects the TierMapper for rank resolution.
        """
        self.tier_mapper = tier_mapper

    MANUAL_ID_MAPPINGS = {
        "Cooked_Prime_Meat": "Cooked_Giant_Steak",
        "Dried_Prime_Meat": "Giant_Steak_Dried",
        "Prime_Animal_Fat": "Animal_Fat",
    }

    def _build_composite_index(self, recipe_rows: list[dict[str, Any]], items_static: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """
        Groups recipes by potential consumable names using multiple resolution strategies.
        """
        from collections import defaultdict
        index = defaultdict(list)
        
        # 1. Map Consumable Trait names to Item Names and Itemable Names using D_ItemsStatic
        consumable_to_item = defaultdict(set)
        for row in items_static:
            item_name = str(row.get("Name", ""))
            consumable_trait = row.get("Consumable", {}).get("RowName", "None")
            itemable_name = row.get("Itemable", {}).get("RowName", "None")
            
            if consumable_trait != "None":
                consumable_to_item[consumable_trait].add(item_name)
                if itemable_name != "None":
                    consumable_to_item[consumable_trait].add(itemable_name)

        # 2. Add Manual Mappings
        for cons_id, target_id in self.MANUAL_ID_MAPPINGS.items():
            consumable_to_item[cons_id].add(target_id)

        # 3. Index recipes by Output Item and Recipe Name
        for row in recipe_rows:
            recipe_name = str(row.get("Name", ""))
            outputs = [str(o.get("Element", {}).get("RowName", "")) for o in row.get("Outputs", [])]
            outputs = [o for o in outputs if o and o != "None"]
            
            # Strategy A: Map by recipe name directly
            index[recipe_name].append(row)
            
            # Strategy B: Map by output item names (with normalization)
            for out_name in outputs:
                index[out_name].append(row)
                norm_out = out_name
                if norm_out.startswith("Food_"): norm_out = norm_out[5:]
                elif norm_out.startswith("Item_"): norm_out = norm_out[5:]
                index[norm_out].append(row)

            # Strategy C: Bridge via Consumable mappings
            for cons_id, item_names in consumable_to_item.items():
                match_found = False
                if recipe_name in item_names:
                    match_found = True
                
                if not match_found:
                    for out_name in outputs:
                        if out_name in item_names:
                            match_found = True
                            break
                        norm_out = out_name
                        if norm_out.startswith("Food_"): norm_out = norm_out[5:]
                        elif norm_out.startswith("Item_"): norm_out = norm_out[5:]
                        if norm_out in item_names:
                            match_found = True
                            break
                
                if match_found:
                    index[cons_id].append(row)

        return index

    def get_recipe_rows_for_item(self, item_name: str) -> list[dict[str, Any]]:
        """
        Returns the raw recipe rows for an item from the index, attempting multiple name variations.
        """
        rows = self.recipe_map.get(item_name, [])
        if rows:
            return rows

        # Try variations to handle inconsistent Food_/Item_ prefixes
        variations = [f"Item_{item_name}", f"Food_{item_name}"]
        if item_name.startswith("Food_"):
            variations.append(item_name[5:])
        if item_name.startswith("Item_"):
            variations.append(item_name[5:])
        
        for v in variations:
            if v in self.recipe_map:
                return self.recipe_map[v]
                
        return []

    def get_recipes_for_item(self, item_name: str) -> list[Recipe]:
        """
        Finds all recipes that produce the specified item, deduplicated and sorted.
        """
        rows = self.get_recipe_rows_for_item(item_name)
        recipes = [self._parse_recipe(row) for row in rows]
        
        deduplicated = self.deduplicate_recipes(recipes)
        
        # Sort benches for each recipe
        for r in deduplicated:
            self.sort_recipe_benches(r)
            
        return deduplicated

    def deduplicate_recipes(self, recipes: list[Recipe]) -> list[Recipe]:
        """
        Ensures logical uniqueness of recipes (same benches, inputs, and outputs).
        """
        seen_keys = set()
        unique_recipes = []
        
        for r in recipes:
            # Create a stable key for identification
            # Benches, Inputs, and Outputs are sorted to ensure consistency
            benches_key = tuple(sorted(r.benches))
            inputs_key = tuple(sorted([
                (ing.item.name if ing.item else ing.tag, ing.count, ing.is_generic) 
                for ing in r.inputs
            ]))
            outputs_key = tuple(sorted([
                (out.item.name, out.count) 
                for out in r.outputs
            ]))
            
            recipe_key = (benches_key, inputs_key, outputs_key)
            
            if recipe_key not in seen_keys:
                seen_keys.add(recipe_key)
                unique_recipes.append(r)
                
        return unique_recipes

    def sort_recipe_benches(self, recipe: Recipe):
        """
        Sorts the benches in a recipe by their technological rank.
        """
        if not self.tier_mapper:
            return
            
        recipe.benches.sort(key=lambda b: self.tier_mapper.get_bench_rank(b))

    def _parse_recipe(self, row: dict[str, Any]) -> Recipe:
        """
        Parses a recipe row into a Recipe object, handling both specific and generic inputs.
        """
        inputs = []
        # 1. Specific Inputs
        for i in row.get("Inputs", []):
            item_name = str(i.get("Element", {}).get("RowName", ""))
            if item_name and item_name != "None":
                inputs.append(Ingredient(
                    item=IcarusItem(item_name, "", ""), 
                    count=int(i.get("Count", 1))
                ))

        # 2. Generic Query Inputs (Phase 6)
        for qi in row.get("QueryInputs", []):
            tag_name = str(qi.get("Tag", {}).get("RowName", ""))
            if tag_name and tag_name != "None":
                display_name = tag_name
                if self.tag_service:
                    display_name = self.tag_service.get_tag_display_name(tag_name)
                
                inputs.append(Ingredient(
                    item=None,
                    count=int(qi.get("Count", 1)),
                    tag=tag_name,
                    is_generic=True
                ))
        
        outputs = [
            Ingredient(IcarusItem(str(o.get("Element", {}).get("RowName", "")), "", ""), int(o.get("Count", 1)))
            for o in row.get("Outputs", [])
            if str(o.get("Element", {}).get("RowName", "")) != "None"
        ]
        
        benches = [str(b.get("RowName")) for b in row.get("RecipeSets", [])]

        return Recipe(
            id=str(row.get("Name")),
            benches=benches,
            inputs=inputs,
            outputs=outputs,
            requirement=str(row.get("Requirement", {}).get("RowName")),
            character_req=row.get("CharacterRequirement"),
            session_req=row.get("SessionRequirement"),
            energy_cost=float(row.get("RequiredMillijoules", 0.0))
        )
