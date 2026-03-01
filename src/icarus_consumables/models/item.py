from dataclasses import dataclass
from typing import Optional

@dataclass
class IcarusItem:
    """
    The fundamental base class for all items in the Icarus game data.
    Stores the core identifiers and localization strings.

    Example:
        >>> item = IcarusItem(
        ...     name="Item_Oxite",
        ...     display_name="Oxite",
        ...     description="A frozen chunk of oxygen-rich ice."
        ... )
    """
    name: str                 # Internal name (e.g., "Food_Meat_Stew")
    display_name: str         # Localized name (e.g., "Meat Stew")
    description: str          # Item flavor text
    yields_item: Optional[str] = None # For items that break down (e.g., Cake -> Piece)
    yields_count: int = 1              # How many are yielded
