import json
from typing import List
from icarus_food.generators.base import BaseGenerator
from icarus_food.models.consumable import ConsumableData

class JsonGenerator(BaseGenerator):
    """Generates structured JSON output with metadata and visibility filtering."""

    def __init__(self, filename: str, parser_version: str = "TBD", game_version: str = "TBD"):
        super().__init__(filename)
        self.parser_version = parser_version
        self.game_version = game_version

    def generate(self, data: List[ConsumableData]) -> None:
        items = []
        for item in data:
            if not item.is_visible:
                continue

            item_dict = {
                "name": item.name,
                "display_name": item.display_name,
                "category": item.category,
                "base_stats": item.base_stats,
                "description": item.description,
                "source_item": item.source_item,
                "tier": {
                    "total": item.tier_info.total_tier,
                    "anchor": item.tier_info.anchor_bench,
                    "is_harvested": item.tier_info.is_harvested,
                    "is_override": item.tier_info.is_override
                },
                "growth_data": {
                    "growth_time": item.growth_time,
                    "harvest_yield": item.harvest_yield
                } if item.growth_time or item.harvest_yield else None,
                "modifiers": [
                    {
                        "id": m.id,
                        "display_name": m.display_name,
                        "effects": m.effects,
                        "lifetime": m.lifetime
                    } for m in item.modifiers
                ],
                "recipes": [
                    {
                        "benches": r.benches,
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
                        "outputs": [
                            {
                                "name": out.item.name, 
                                "yields_count": out.count * item.yield_multiplier, 
                                "display_name": out.item.display_name,
                                "yields_item": out.item.yields_item
                            } for out in r.outputs
                        ],
                        "requirements": {
                            "talent": r.requirement,
                            "character": r.character_req,
                            "session": r.session_req
                        }
                    } for r in item.recipes
                ]
            }
            items.append(item_dict)

        output = {
            "metadata": {
                "parser_version": self.parser_version,
                "game_version": self.game_version
            },
            "items": items
        }

        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4)
