import json
from pathlib import Path
from typing import List
from icarus_consumables.generators.base import BaseGenerator
from icarus_consumables.models.consumable import ConsumableData

class JsonGenerator(BaseGenerator):
    """Generates structured JSON output with metadata and visibility filtering."""

    def __init__(self, filename: str, parser_version: str = "TBD", game_version: str = "TBD"):
        super().__init__(filename)
        self.parser_version = parser_version
        self.game_version = game_version
        self.stat_metadata_map = self._load_stat_metadata()

    def _load_stat_metadata(self) -> dict:
        """Loads stat labels and categories from external mapping file."""
        # Look for data directory in project root
        data_path = Path("data/stat_metadata.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # Fallback to current directory for safety if needed
            return {}

    def generate(self, data: List[ConsumableData]) -> None:
        items = []
        modifiers_map = {}
        recipes_map = {}
        used_stats = set()
        
        # Build mapping for 'Primary' recipe detection
        consumable_names = {item.name for item in data}
        yields_map = {item.name: item.yields_item for item in data if item.yields_item}

        for item in data:
            if not item.is_visible:
                continue

            # 1. Process Modifiers
            item_modifier_ids = []
            for m in item.modifiers:
                if m is None or not m.id:
                    continue
                item_modifier_ids.append(m.id)
                if m.id not in modifiers_map:
                    # Convert list of StatEffect objects to JSON dictionary
                    mod_effects = {}
                    for effect in m.effects:
                        key, val = effect.to_json_pair()
                        mod_effects[key] = val
                        # Track which non-suffixed stat names are used
                        used_stats.add(effect.name)

                    modifiers_map[m.id] = {
                        "id": m.id,
                        "display_name": m.display_name,
                        "effects": mod_effects,
                        "lifetime": m.lifetime,
                        "description": m.description
                    }

            # 2. Process Recipes with 'Primary' Filtering & Grouping
            primary_recipes = []
            for r in item.recipes:
                is_primary = False
                # If item is harvested (Tier 0), we keep all recipes for completeness
                if item.tier_info.is_harvested:
                    is_primary = True
                elif len(r.outputs) == 1:
                    is_primary = True
                else:
                    found_superior_consumable = False
                    for out in r.outputs:
                        if out.item.name == item.name:
                            continue
                        # Check if another output (e.g. Gamey_Meat) yields us (Raw Meat)
                        # ONLY suppress if the other output is ALSO being exported as a consumable
                        if out.item.yields_item == item.name and out.item.name in consumable_names:
                            found_superior_consumable = True
                            break
                    if not found_superior_consumable:
                        is_primary = True
                
                if is_primary:
                    primary_recipes.append(r)

            # Group recipes by (Consumable Outputs + Benches)
            grouped_item_recipes = []
            signatures = {} # (ConsumableOutputsSig, BenchesSig) -> GroupData

            for r in primary_recipes:
                # Signature is based ONLY on consumable outputs
                cons_outputs = []
                res_outputs = []
                for o in r.outputs:
                    # Treat as consumable if it's in our export list OR if it yields another consumable
                    if o.item.name in consumable_names or o.item.yields_item:
                        cons_outputs.append((o.item.name, o.count, o.item.display_name, o.item.yields_item))
                    else:
                        res_outputs.append((o.item.name, o.count))
                
                cons_sig = tuple(sorted(cons_outputs, key=lambda x: x[0]))
                benches_sig = tuple(sorted(r.benches))
                sig = (cons_sig, benches_sig)

                if sig in signatures:
                    group = signatures[sig]
                    # Update alternate inputs
                    existing_alternate_names = {i['name'] for i in group['alternate_inputs']}
                    existing_primary_names = {i['name'] for i in group['inputs']}
                    
                    for ing in r.inputs:
                        ing_name = ing.item.name if ing.item else ing.tag
                        if ing_name not in existing_alternate_names and ing_name not in existing_primary_names:
                            group['alternate_inputs'].append({
                                "name": ing_name,
                                "count": ing.count,
                                "display_name": ing.item.display_name if ing.item else (
                                    ing.tag.replace("Any_", "").replace("_", " ") if ing.tag else "Unknown"
                                ),
                                "is_generic": ing.is_generic
                            })
                    
                    # Accumulate resource yields for range calculation
                    for res_name, res_count in res_outputs:
                        if res_name not in group['_res_yields']:
                            group['_res_yields'][res_name] = []
                        group['_res_yields'][res_name].append(res_count)
                else:
                    # Create new group
                    group = {
                        "id": r.id, 
                        "benches": list(benches_sig),
                        "inputs": [
                            {
                                "name": ing.item.name if ing.item else ing.tag, 
                                "count": ing.count, 
                                "display_name": ing.item.display_name if ing.item else (
                                    ing.tag.replace("Any_", "").replace("_", " ") if ing.tag else "Unknown"
                                ),
                                "is_generic": ing.is_generic
                            } for ing in r.inputs
                        ],
                        "alternate_inputs": [],
                        "outputs": [], # Will be populated after processing all
                        "requirements": {
                            "talent": r.requirement,
                            "character": r.character_req,
                            "session": r.session_req
                        },
                        "_cons_outputs": cons_outputs,
                        "_res_yields": {name: [count] for name, count in res_outputs}
                    }
                    signatures[sig] = group
                    grouped_item_recipes.append(group)

            item_recipe_ids = []
            for group in grouped_item_recipes:
                # Finalize outputs with ranges and averages
                final_outputs = []
                
                # Consumables are exact matches in this group
                for name, count, display, yield_item in group["_cons_outputs"]:
                    final_outputs.append({
                        "name": name,
                        "yields_count": count * item.yield_multiplier,
                        "display_name": display,
                        "yields_item": yield_item
                    })

                # Resources (non-consumables) can vary
                for name, counts in group["_res_yields"].items():
                    min_y = min(counts)
                    max_y = max(counts)
                    avg_y = sum(counts) / len(counts)
                    
                    res_out = {
                        "name": name,
                        "yields_count": round(avg_y * item.yield_multiplier, 1),
                        "display_name": name.replace("_", " ") # Fallback
                    }
                    
                    if min_y != max_y:
                        res_out["yields_min"] = round(min_y * item.yield_multiplier, 1)
                        res_out["yields_max"] = round(max_y * item.yield_multiplier, 1)
                    
                    final_outputs.append(res_out)

                group["outputs"] = final_outputs
                
                # Clean up internal tracking fields and optimize schema
                del group["_cons_outputs"]
                del group["_res_yields"]
                if not group["alternate_inputs"]:
                    del group["alternate_inputs"]

                rid = group["id"]
                item_recipe_ids.append(rid)
                if rid not in recipes_map:
                    recipes_map[rid] = group

            # Refactor traits: Group booleans and omit false values for optimization
            traits = {}
            if item.tier_info.is_harvested: traits["is_harvested"] = True
            if item.tier_info.is_orbital: traits["is_orbital"] = True
            if item.is_decay_product: traits["is_decay_product"] = True
            if item.is_override: traits["is_override"] = True

            item_dict = {
                "name": item.name,
                "display_name": item.display_name,
                "category": item.category,
                "description": item.description,
                "traits": traits if traits else None,
                "source_item": item.source_item,
                "source_ids": item.source_ids,
                "tier": {
                    "total": item.tier_info.total_tier,
                    "anchor": item.tier_info.anchor_bench
                },
                "growth_data": {
                    "growth_time": item.growth_time,
                    "harvest_min": item.harvest_min,
                    "harvest_max": item.harvest_max
                } if item.growth_time or (item.harvest_min is not None) else None,
                "base_stats": item.base_stats,
                "modifiers": item_modifier_ids,
                "recipes": item_recipe_ids
            }
            # Remove traits if None to save even more space
            if item_dict["traits"] is None:
                del item_dict["traits"]

            items.append(item_dict)

        # 3. Build Stat Metadata
        stat_metadata = {}
        for stat in sorted(used_stats):
            meta = self.stat_metadata_map.get(stat)
            if meta:
                stat_metadata[stat] = meta
            else:
                # Fallback for unknown stats
                clean_label = stat.replace("Base", "").replace("_", " ")
                stat_metadata[stat] = {
                    "label": clean_label,
                    "categories": ["Other"]
                }

        # 4. Write Separate Files
        metadata = {
            "parser_version": self.parser_version,
            "game_version": self.game_version
        }

        # Items
        items_path = self.output_path.parent / "consumables_items.json"
        with open(items_path, 'w', encoding='utf-8') as f:
            json.dump({"metadata": metadata, "items": items}, f, indent=4)

        # Recipes
        recipes_path = self.output_path.parent / "consumables_recipes.json"
        with open(recipes_path, 'w', encoding='utf-8') as f:
            json.dump({"metadata": metadata, "recipes": recipes_map}, f, indent=4)

        # Modifiers
        modifiers_path = self.output_path.parent / "consumables_modifiers.json"
        with open(modifiers_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": metadata, 
                "stat_metadata": stat_metadata,
                "modifiers": modifiers_map
            }, f, indent=4)

        # Legacy cleanup/fallback (optional, but requested separate for now)
        # We'll stop writing the monolithic file as requested.
