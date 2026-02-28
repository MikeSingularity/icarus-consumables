from dataclasses import dataclass
from typing import Any

@dataclass
class ModifierEffect:
    """
    Defines a status effect or buff applied to a player, typically from 
    consuming food or medicine. Includes the duration and specific stat changes.

    Example:
        >>> modifier = ModifierEffect(
        ...     id="Buff_WellFed",
        ...     display_name="Well Fed",
        ...     description="Increased stamina and health regeneration.",
        ...     lifetime=900,
        ...     effects={"MaxStamina": 50.0, "HealthRegen": 2.0}
        ... )
    """
    id: str                   # Modifier row name (e.g., "Bread")
    display_name: str         # Localized name (e.g., "Bready Goodness")
    description: str          # Flavor description or effect summary
    lifetime: int             # Duration in seconds
    effects: dict[str, float] # Stat bonuses (e.g., {"MaxStamina": 100})
