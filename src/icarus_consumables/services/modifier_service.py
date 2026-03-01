import re
from typing import Any, Optional
from icarus_consumables.models.modifier import ModifierEffect, StatEffect, StatType

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
        # Captures: 1. Stat name, 2. Suffix (e.g. _+%, _%, _?, _+)
        self.stat_pattern = re.compile(r'Value="(.+?)(_\+%|_%|_\?|_\+)"')

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
        effects: list[StatEffect] = []
        for stat_key, value in row.get("GrantedStats", {}).items():
            match = self.stat_pattern.search(str(stat_key))
            if match:
                clean_name = match.group(1)
                suffix = match.group(2)
                
                stat_type = StatType.FLAT
                if "%" in suffix:
                    stat_type = StatType.PERCENTAGE
                elif "?" in suffix:
                    stat_type = StatType.BOOLEAN
                
                effects.append(StatEffect(
                    name=clean_name,
                    stat_type=stat_type,
                    value=value
                ))
            else:
                # Fallback for unexpected formats
                effects.append(StatEffect(
                    name=str(stat_key),
                    stat_type=StatType.FLAT,
                    value=value
                ))

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
