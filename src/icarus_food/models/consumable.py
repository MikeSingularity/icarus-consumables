from dataclasses import dataclass, field
from typing import Optional
from .item import IcarusItem
from .modifier import ModifierEffect
from .recipe import Recipe
from .tier import TierInfo

@dataclass
class ConsumableData(IcarusItem):
    """
    Represents the full set of data for a consumable item in Icarus, 
    including its stats, modifiers, crafting recipes, and tier information.

    Example:
        >>> consumable = ConsumableData(
        ...     name="Food_Meat_Stew",
        ...     display_name="Meat Stew",
        ...     description="A hearty stew made from various meats.",
        ...     category="Food",
        ...     base_stats={"Food": 50.0, "Health": 20.0},
        ...     modifiers=[ModifierEffect(id="Stew_Buff", ...)],
        ...     recipes=[Recipe(id="Recipe_Meat_Stew", ...)],
        ...     tier_info=TierInfo(base_tier=2, total_tier=2.3, ...)
        ... )
    """
    category: str = ""
    is_visible: bool = True
    base_stats: dict[str, float] = field(default_factory=dict)
    modifiers: list[ModifierEffect] = field(default_factory=list)
    recipes: list[Recipe] = field(default_factory=list)
    tier_info: TierInfo = field(default_factory=lambda: TierInfo(0, 0.0, 0.0, "None", True))
    
    # Growth Data
    growth_time: Optional[int] = None
    harvest_yield: Optional[str] = None
    yield_multiplier: int = 1
    source_item: Optional[str] = None # The item this piece came from (e.g., Chocolate_Cake)
