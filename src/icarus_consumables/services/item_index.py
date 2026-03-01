import re
import logging
import json
import os
from pathlib import Path
from typing import Optional, Dict, Tuple, List, Any

# Configure logger for this module
logger = logging.getLogger(__name__)

class ItemIndexService:
    """
    Acts as the master index for resolving item IDs across different game data files 
    (D_ItemsStatic, D_Consumable, etc.). Uses a dual-dictionary approach to align 
    various source IDs to a single normalized concept.
    """

    def __init__(self):
        """
        Initializes the Item Index.
        """
        # Primary lookup: (SourceFile, SourceId) -> NormalizedId
        self.source_to_norm: Dict[Tuple[str, str], str] = {}
        
        # Reverse lookup: NormalizedId -> {SourceFile: SourceId}
        self.norm_to_source: Dict[str, Dict[str, str]] = {}
        
        # Only non-state prefixes should be stripped to prevent collapsing Raw/Cooked
        self.prefixes_to_strip = [
            "Food_",
            "Drink_",
            "Item_"
        ]

    def _normalize_id(self, source_id: str) -> str:
        """
        Strips known structural prefixes, lowers cases, and removes non-alphanumerics.
        """
        norm_id = source_id
        for prefix in self.prefixes_to_strip:
            if norm_id.startswith(prefix):
                norm_id = norm_id[len(prefix):]
                break # Only strip one prefix
                
        norm_id = norm_id.lower()
        norm_id = re.sub(r'[^a-z0-9]', '', norm_id)
        
        return norm_id

    def add_entry(self, source_file: str, source_id: str):
        """
        Indexes an item ID from a specific source file, updating both dictionaries.
        """
        if not source_id or source_id == "None":
            return
            
        norm_id = self._normalize_id(source_id)
        
        # 1. Update Primary Lookup
        self.source_to_norm[(source_file, source_id)] = norm_id
        
        # 2. Update Reverse Lookup (with collision detection)
        if norm_id not in self.norm_to_source:
            self.norm_to_source[norm_id] = {}
            
        existing_entry = self.norm_to_source[norm_id].get(source_file)
        if existing_entry and existing_entry != source_id:
            logger.warning(
                f"INDEX COLLISION: Normalized ID '{norm_id}' in '{source_file}' "
                f"already points to '{existing_entry}'. Refusing to overwrite with '{source_id}'."
            )
            return
            
        self.norm_to_source[norm_id][source_file] = source_id

    def get_normalized_id(self, source_file: str, source_id: str) -> Optional[str]:
        """
        Returns the normalized internal ID for a given exact source ID.
        """
        return self.source_to_norm.get((source_file, source_id))

    def get_source_id(self, target_source_file: str, normalized_id: str) -> Optional[str]:
        """
        Returns the exact source file ID for a normalized ID, if it exists in that file.
        """
        if normalized_id not in self.norm_to_source:
            return None
        return self.norm_to_source[normalized_id].get(target_source_file)
        
    def translate_id(self, from_source_file: str, to_source_file: str, source_id: str) -> Optional[str]:
        """
        Convenience method: Translates an ID from one file directly into its counterpart in another file.
        """
        norm_id = self.get_normalized_id(from_source_file, source_id)
        if not norm_id:
            # If not formally indexed by the original file, just calculate the heuristic
            norm_id = self._normalize_id(source_id)
            
        return self.get_source_id(to_source_file, norm_id)

    def export_to_json(self, filepath: str):
        """
        Exports the entire norm_to_source mapping to a volatile JSON file 
        for debugging, index visibility, and cache jumpstarting.
        """
        export_data = {
            "metadata": {
                "generated_by": "ItemIndexService",
                "description": "Maps normalized IDs back to their specific source file IDs."
            },
            "norm_to_source": self.norm_to_source
        }
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=4, sort_keys=True)
            logger.info(f"Item Index exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export Item Index to {filepath}: {e}")
