from typing import Any

class CategoryService:
    """
    Handles the classification of Icarus items into categories (Food, Drink, 
    Medicine, Animal Food). This logic is isolated to allow for frequent 
    game-balance updates without modifying the core parser.
    """

    def __init__(self, processing_config: dict[str, Any]):
        """
        Initializes the service with configuration rules.
        """
        self.config = processing_config

    def assign_category(self, name: str, stats: dict[str, float]) -> str:
        """
        Determines the category for a given item name and its base stats.
        
        Logic (Priority Order):
        1. Animal Food: Has Food stats and "Animal/Omni" in name.
        2. Food: Has Food recovery stats.
        3. Drink: Has Water recovery stats.
        4. Medicine: Default for all other consumables (Bandages, Oxygen, etc.).
        """
        if "Food" in stats:
            if "Animal" in name or "Omni" in name:
                return "Animal Food"
            return "Food"
            
        if "Water" in stats:
            # Special case for some medicine/utility that might have water? 
            # Currently standard Drink definition.
            return "Drink"
            
        return "Medicine"
