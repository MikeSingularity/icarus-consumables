import re
from typing import Any, Optional

def clean_id(name: str) -> str:
    """
    Normalizes a game identifier for consistent lookups.
    """
    return name.strip()

class IcarusTranslationService:
    """
    Resolves internal game identifiers (e.g., Food_Meat_Stew) to their 
    localized display names and descriptions. Handles common naming 
    conventions and extracts text from localized string formats.
    """
    cleanup_pattern = re.compile(r'^(Food_|Drink_|Item_|Kit_|Dough_)?(.*)$')
    loc_pattern = re.compile(r'NSLOCTEXT\(".*?",\s*".*?",\s*"(.*?)"\)')

    def __init__(self, itemable_rows: list[dict[str, Any]], items_static: list[dict[str, Any]] = []):
        """
        Initializes the translation service with mappings from game data.
        """
        self.translation_map, self.description_map, self.yield_map = self._build_maps(itemable_rows, items_static)

    def _build_maps(self, itemable_rows: list[dict[str, Any]], items_static: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, str], dict[str, tuple[str, int]]]:
        """
        Builds mappings from internal Name to resolved DisplayName, Description, and Yield info.
        """
        trans_mapping: dict[str, str] = {}
        desc_mapping: dict[str, str] = {}
        yield_mapping: dict[str, tuple[str, int]] = {}

        for row in itemable_rows:
            name: str = str(row.get("Name", ""))
            if not name:
                continue

            # Display Name
            display_name_raw: str = str(row.get("DisplayName", ""))
            match = self.loc_pattern.search(display_name_raw)
            trans_mapping[name] = match.group(1) if match else display_name_raw

            # Description
            desc_raw = str(row.get("Description", ""))
            match = self.loc_pattern.search(desc_raw)
            desc_mapping[name] = match.group(1) if match else desc_raw

        for row in items_static:
            name = str(row.get("Name"))
            cons = row.get("Consumable", {})
            child_name = str(cons.get("RowName", ""))
            if child_name and child_name != "None" and child_name != name:
                # We don't have a direct "yield count" in ItemsStatic for cakes, 
                # but we can default to 1 and let overrides handle it.
                yield_mapping[name] = (child_name, 1)

        return trans_mapping, desc_mapping, yield_mapping

    def get_yield_info(self, internal_name: str) -> Optional[tuple[str, int]]:
        """Returns the item yielded by this item and its count."""
        return self.yield_map.get(internal_name)

    def get_display_name(self, internal_name: str) -> str:
        """
        Translates an internal name to a display name with fallback cleanup.
        """
        # 1. Direct match
        if internal_name in self.translation_map:
            return self.translation_map[internal_name]
        
        # 2. Try Item_[InternalName]
        alt_name = f"Item_{internal_name}"
        if alt_name in self.translation_map:
            return self.translation_map[alt_name]

        # 3. Try stripping common prefixes for fallback
        match = self.cleanup_pattern.match(internal_name)
        if match:
            return match.group(2).replace('_', ' ')
        
        return internal_name.replace('_', ' ')

    def get_description(self, internal_name: str, itemable_rows: list[dict[str, Any]] = []) -> str:
        """
        Extracts description text from indexed mapping.
        """
        if internal_name in self.description_map:
            return self.description_map[internal_name]
        
        alt_name = f"Item_{internal_name}"
        if alt_name in self.description_map:
            return self.description_map[alt_name]

        return ""
