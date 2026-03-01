import json
from pathlib import Path
from typing import Any, Optional

class OverrideService:
    """
    Manages item property overrides loaded from template files.
    Allows for manual correction of game data, visibility toggling, 
    and tier overrides.
    """

    def __init__(self, overrides_dir: str = "data/overrides"):
        """
        Initializes the service by loading all JSON files in the overrides directory.
        """
        self.overrides: dict[str, dict[str, Any]] = {}
        self._load_overrides(overrides_dir)

    def get_all_overridden_items(self) -> list[str]:
        """Returns a list of all item names that have overrides."""
        return list(self.overrides.keys())

    def _load_overrides(self, overrides_dir: str):
        """
        Scans the overrides directory for JSON files and merges them.
        """
        dir_path = Path(overrides_dir)
        if not dir_path.exists():
            return

        for file_path in dir_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Merge overrides, later files take precedence if there are collisions
                        # (alphabetical order of filenames determines precedence here)
                        self.overrides.update(data)
            except Exception as e:
                print(f"Warning: Failed to load override file {file_path}: {e}")

    def get_override(self, item_name: str) -> dict[str, Any]:
        """
        Returns the override dictionary for a given item name if it exists.
        Supports case-insensitive lookup.
        """
        # Try direct match
        if item_name in self.overrides:
            return self.overrides[item_name]
        
        # Try lowercase match
        for key, value in self.overrides.items():
            if key.lower() == item_name.lower():
                return value
                
        return {}

    def apply_overrides(self, item_name: str, item_data: Any):
        """
        Applies configured overrides to a ConsumableData object.
        """
        overrides = self.get_override(item_name)
        if not overrides:
            return

        # Mark as overridden
        item_data.is_override = True

        # Visibility
        if "is_visible" in overrides:
            item_data.is_visible = overrides["is_visible"]

        # Yield Multiplier
        if "yield_multiplier" in overrides:
            item_data.yield_multiplier = int(overrides["yield_multiplier"])

        # Tier
        if "tier" in overrides and hasattr(item_data, "tier_info"):
            item_data.tier_info.total_tier = float(overrides["tier"])

        # Stats
        if "stats" in overrides and hasattr(item_data, "base_stats"):
            item_data.base_stats.update(overrides["stats"])

        # Description
        if "description" in overrides:
            item_data.description = overrides["description"]

        # Display Name
        if "display_name" in overrides:
            item_data.display_name = overrides["display_name"]
