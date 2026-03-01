from typing import Any, Optional, Dict, List
import re

class IcarusTagService:
    """
    Resolves generic crafting tags (e.g., Any_Vegetable) to their 
    localized names and provides mapping to items that satisfy them.
    """

    def __init__(self, crafting_tags: List[Dict[str, Any]], tag_queries: List[Dict[str, Any]]):
        """
        Initializes the tag service with data from D_CraftingTags and D_TagQueries.
        """
        self.tags = {str(row["Name"]): row for row in crafting_tags}
        self.queries = {str(row["Name"]): row for row in tag_queries}
        self.loc_pattern = re.compile(r'NSLOCTEXT\(".*?",\s*".*?",\s*"(.*?)"\)')

    def get_tag_display_name(self, tag_name: str) -> str:
        """
        Translates a generic tag name (Any_Vegetable) to its display name (Vegetable).
        """
        tag = self.tags.get(tag_name)
        if not tag:
            return tag_name.replace("Any_", "").replace("_", " ")

        display_raw = str(tag.get("TagName", ""))
        match = self.loc_pattern.search(display_raw)
        return match.group(1) if match else display_raw

    def get_query_for_tag(self, tag_name: str) -> Optional[str]:
        """
        Returns the query associated with a crafting tag.
        """
        tag = self.tags.get(tag_name)
        if not tag:
            return None
        return str(tag.get("Query", {}).get("RowName"))

    def get_satisfying_tags_for_query(self, query_name: str) -> List[str]:
        """
        Returns a list of specific GameplayTags that satisfy a given query.
        For simple ANY/ALL queries, this is often a 1:1 mapping.
        """
        query = self.queries.get(query_name)
        if not query:
            return []

        # Most generic food tags use a simple ANY or ALL query with a single tag
        tag_dict = query.get("Query", {}).get("TagDictionary", [])
        return [str(t.get("TagName")) for t in tag_dict]
