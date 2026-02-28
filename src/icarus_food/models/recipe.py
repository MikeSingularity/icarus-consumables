from dataclasses import dataclass
from typing import Optional
from .item import IcarusItem

@dataclass
class Ingredient:
    """
    A link between an item and a specific quantity, used for defining 
    recipe inputs (ingredients) and outputs.

    Example:
        >>> ingredient = Ingredient(
        ...     item=IcarusItem(name="Raw_Meat", ...),
        ...     count=2
        ... )
    """
    item: Optional[IcarusItem] = None # Specific item (None if generic)
    count: int = 1                    # Quantity required or produced
    tag: Optional[str] = None         # For generic inputs (e.g., Any_Vegetable)
    is_generic: bool = False          # Whether this is a generic tag-based input

@dataclass
class Recipe:
    """
    A complete crafting recipe definition, mapping inputs to outputs 
    and specifying where and how the item can be made.

    Example:
        >>> recipe = Recipe(
        ...     id="Recipe_Cooked_Meat",
        ...     benches=["Campfire", "Firepit"],
        ...     inputs=[Ingredient(item=Raw_Meat, count=1)],
        ...     outputs=[Ingredient(item=Cooked_Meat, count=1)],
        ...     energy_cost=0.0
        ... )
    """
    id: str                   # Recipe row name (e.g., "Food_Meat_Stew")
    benches: list[str]        # List of benches where this can be crafted
    inputs: list[Ingredient]  # Items required for crafting
    outputs: list[Ingredient] # Items produced
    requirement: Optional[str] = None      # Talent requirement
    character_req: Optional[str] = None    # Character flag requirement
    session_req: Optional[str] = None      # DLC or mission requirements
    energy_cost: float = 0.0               # Required millijoules
