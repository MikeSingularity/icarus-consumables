from dataclasses import dataclass
from enum import Enum
from typing import Any, Tuple

class StatType(Enum):
    """Enumeration of modifier effect types."""
    FLAT = "flat"
    PERCENTAGE = "percentage"
    BOOLEAN = "boolean"

@dataclass
class StatEffect:
    """
    Represents a single stat change from a modifier.
    """
    name: str
    stat_type: StatType
    value: Any

    def to_json_pair(self) -> Tuple[str, Any]:
        """
        Converts this effect into a key-value pair for JSON output.
        - Percentages are suffixed with '%' and scaled by 100.
        - Booleans remain as-is.
        - Flat values remain as-is.
        """
        if self.stat_type == StatType.PERCENTAGE:
            return f"{self.name}%", round(self.value / 100.0, 4)
        elif self.stat_type == StatType.BOOLEAN:
            # Game data often uses 1 for True, but we want real booleans
            return self.name, bool(self.value)
        
        return self.name, float(self.value)

@dataclass
class ModifierEffect:
    """
    Defines a status effect or buff applied to a player.
    """
    id: str                   # Modifier row name (e.g., "Bread")
    display_name: str         # Localized name
    description: str          # Flavor description
    lifetime: int             # Duration in seconds
    effects: list[StatEffect] # Structured stat effects
