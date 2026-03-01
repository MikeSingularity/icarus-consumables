import re
from typing import Any, Optional
from icarus_consumables.models.modifier import ModifierEffect

class ModifierService:
    """
    Handles the resolution and parsing of status effects (modifiers). 
    Matches modifier IDs from consumable data to their definitions in the 
    game's modifier state files, extracting localized text and stat changes.
    """

    def __init__(self, modifier_rows: list[dict[str, Any]]):
        """
        Initializes the service with modifier data from game files.
        """
        self.modifiers = {str(row.get("Name")): row for row in modifier_rows}
        self.loc_pattern = re.compile(r'NSLOCTEXT\(".*?",\s*".*?",\s*"(.*?)"\)')

    def get_modifier_effect(self, modifier_id: str, lifetime: int) -> Optional[ModifierEffect]:
        """
        Resolves a modifier ID to a ModifierEffect object.
        """
        if modifier_id not in self.modifiers:
            return None
        
        row = self.modifiers[modifier_id]
        
        # Extract DisplayName and Description
        name_raw = str(row.get("ModifierName", ""))
        desc_raw = str(row.get("ModifierDescription", ""))
        
        display_name = self._translate(name_raw) or modifier_id
        description = self._translate(desc_raw) or ""
        
        # Parse stat effects
        effects: dict[str, Any] = {}
        for stat_key, value in row.get("Stats", {}).items():
            # Key format: (Value="StatName_+") or similar
            match = re.search(r'Value="(.*?)_.*?"', str(stat_key))
            if match:
                clean_key = match.group(1)
                effects[clean_key] = value
            else:
                effects[str(stat_key)] = value

        return ModifierEffect(
            id=modifier_id,
            display_name=display_name,
            description=description,
            lifetime=lifetime,
            effects=effects
        )

    def _translate(self, text: str) -> str:
        """
        Helper to extract text from NSLOCTEXT.
        """
        match = self.loc_pattern.search(text)
        return match.group(1) if match else text
