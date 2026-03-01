import json
from typing import Any
from icarus_consumables.utils.path_resolver import resolve_path

class IcarusDataLoader:
    """
    Provides methods for loading and preliminary validation of Icarus JSON data 
    files extracted from the game's .pak files. Handles path resolution and 
    file reading with proper encoding.
    """

    def __init__(self, pak_dir: str = "unpacked_icarus_data"):
        """
        Initializes the data loader with the pak directory path.
        """
        self.pak_dir = resolve_path(pak_dir)

    def load_json(self, relative_path: str) -> list[dict[str, Any]]:
        """
        Loads a JSON file and returns the Rows list.
        """
        file_path = self.pak_dir / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"Game data file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            return data.get("Rows", [])

    def load_all_data(self) -> dict[str, list[dict[str, Any]]]:
        """
        Loads all required game data files.
        """
        return {
            "consumables": self.load_json("Traits/D_Consumable.json"),
            "recipes": self.load_json("Crafting/D_ProcessorRecipes.json"),
            "recipe_sets": self.load_json("Crafting/D_RecipeSets.json"),
            "modifiers": self.load_json("Modifiers/D_ModifierStates.json"),
            "items_static": self.load_json("Items/D_ItemsStatic.json"),
            "itemable": self.load_json("Traits/D_Itemable.json"),
            "talents": self.load_json("Talents/D_Talents.json"),
            "character_flags": self.load_json("Flags/D_CharacterFlags.json"),
            "farming_seeds": self.load_json("Farming/D_FarmingSeeds.json"),
            "farming_growth_states": self.load_json("Farming/D_FarmingGrowthStates.json"),
            "item_rewards": self.load_json("Items/D_ItemRewards.json"),
            "crafting_tags": self.load_json("Crafting/D_CraftingTags.json"),
            "tag_queries": self.load_json("Tags/D_TagQueries.json")
        }
