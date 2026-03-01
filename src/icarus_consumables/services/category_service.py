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

    def assign_category(self, name: str, stats: dict[str, float], is_orbital: bool = False) -> str:
        """
        Determines the category for a given item name and its base stats.
        
        Follows the priority logic in docs/categories.md:
        1. AnimalFood: Has Food recovery > 0 and "Animal/Omni" in name.
        2. Food item: Has Food/Water recovery > 0 or starts with "Drink_".
        3. Workshop item: Has specific keywords or is an orbital item.
        4. Medicine item: Fallback for all other consumables.
        """
        # 1: Animal Food
        food_recovery = stats.get("Food", 0.0)
        water_recovery = stats.get("Water", 0.0)
        
        # Priority 1: Animal Food
        if food_recovery > 0 and ("Animal" in name or "Omni" in name):
            return "AnimalFood"
            
        # Priority 2: Food
        if food_recovery > 0:
            return "Food"
            
        # Priority 3: Drink
        if water_recovery > 0 or name.startswith("Drink_"):
            return "Drink"
            
        # Priority 4: Workshop (Includes Orbital Seed Packets)
        workshop_keywords = ["_Ammo", "_Arrow", "Biolab_", "_Bolt", "_Resource_Pack"]
        if is_orbital or any(kw in name for kw in workshop_keywords):
            return "Workshop"
            
        # Priority 5: Medicine (Fallback)
        return "Medicine"
