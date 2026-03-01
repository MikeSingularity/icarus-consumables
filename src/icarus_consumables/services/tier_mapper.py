from typing import Any, Optional, Set
from collections import deque
from icarus_consumables.models.tier import TierInfo

class IcarusTierMapper:
    """
    Calculates item tiers by analyzing technology tree progression. 
    It builds a dependency graph of talents to determine how far into 
    a specific crafting tier an item resides, providing a granular 
    total_tier score.
    """

    # Primary technology tier anchors in the talent tree
    ANCHORS = {
        "Character": 1,
        "Crafting_Bench": 2,
        "Machine_Bench": 3,
        "Fabricator": 4
    }

    def __init__(self, item_index: Any, talent_rows: list[dict[str, Any]], recipe_service: Any):
        """
        Initializes the mapper by building talent graphs and item maps.
        """
        self.item_index = item_index
        self.talent_graph = self._build_talent_graph(talent_rows)
        self.talent_parents = self._build_talent_parents(talent_rows)
        self.recipe_service = recipe_service
        self.item_to_talent = self._map_items_to_talents(talent_rows)
        self._anchor_cache: dict[str, str] = {}

    def _build_talent_graph(self, talent_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
        """
        Builds a dependency graph where prerequisites point to dependents.
        """
        graph: dict[str, list[str]] = {}
        for row in talent_rows:
            name = str(row.get("Name"))
            reqs = row.get("RequiredTalents", [])
            for req in reqs:
                prereq = str(req.get("RowName"))
                if prereq not in graph:
                    graph[prereq] = []
                graph[prereq].append(name)
        return graph

    def _build_talent_parents(self, talent_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
        """
        Builds a map from talent to its prerequisites.
        """
        parents: dict[str, list[str]] = {}
        for row in talent_rows:
            name = str(row.get("Name"))
            reqs = row.get("RequiredTalents", [])
            parents[name] = [str(req.get("RowName")) for req in reqs]
        return parents


    def _map_items_to_talents(self, talent_rows: list[dict[str, Any]]) -> dict[str, str]:
        """
        Maps item names and talent names to the talent ID for resolution.
        """
        mapping: dict[str, str] = {}
        for row in talent_rows:
            talent_name = str(row.get("Name"))
            # Map talent name to itself for direct lookup
            mapping[talent_name] = talent_name
            
            item_raw = row.get("ExtraData", {}).get("RowName", "")
            if item_raw:
                # Remove prefixes like Item_ or Kit_
                item_name = item_raw.replace("Item_", "").replace("Kit_", "")
                mapping[item_name] = talent_name
        return mapping

    def calculate_tier(self, item_name: str, recipe_row: Optional[dict[str, Any]]) -> TierInfo:
        """
        Determines the TierInfo for a given item and its recipe.
        """
        # Systematic Harvest Detection via Tags
        is_harvested = False
        item_raw = self.item_index.get(item_name) or self.item_index.get(f"Item_{item_name}")
        if item_raw:
            tags = [t.get("TagName", "") for t in item_raw.get("Manual_Tags", {}).get("GameplayTags", [])] + \
                   [t.get("TagName", "") for t in item_raw.get("Generated_Tags", {}).get("GameplayTags", [])]
            
            harvest_prefixes = [
                "Item.Creature.Loot",       # Meats, Skins, etc.
                "Item.Plant",               # Fruits, Vegetables
                "Item.Resource",            # World resources
                "NPC.Fish",                 # Catchable fish
                "Item.Consumable.Food.Raw"  # Raw gathering items
            ]
            
            if any(any(t.startswith(prefix) for prefix in harvest_prefixes) for t in tags):
                is_harvested = True

        # Tier 0 check: If item is definitely harvested (via tags) or never an output
        is_recipe_output = item_name in self.recipe_service.recipe_map or \
                           f"Item_{item_name}" in self.recipe_service.recipe_map

        if is_harvested or (not is_recipe_output and not recipe_row):
            return TierInfo(0, 0.0, 0.0, "None", True)

        if not recipe_row:
            return TierInfo(0, 0.0, 0.0, "None", True)

        # 2. Find the lowest bench anchor
        benches = recipe_row.get("RecipeSets", [])
        best_anchor_tier = 5
        best_anchor = "None"
        
        for b_ref in benches:
            b_name = b_ref.get("RowName")
            anchor = self._resolve_bench_anchor(b_name)
            tier = self.ANCHORS.get(anchor, 4)
            if tier < best_anchor_tier:
                best_anchor_tier = tier
                best_anchor = anchor

        # 3. Calculate fractional offset from talent tree depth
        talent_name = recipe_row.get("Requirement", {}).get("RowName", "None")
        offset = 0.0
        if talent_name != "None" and best_anchor != "None":
            dist = self._get_talent_distance(best_anchor, talent_name)
            offset = min(dist * 0.1, 0.9)

        total_tier = best_anchor_tier + offset
        return TierInfo(best_anchor_tier, offset, total_tier, best_anchor, False)

    def _resolve_bench_anchor(self, bench_name: str) -> str:
        """
        Dynamically finds the technology anchor for a given bench name.
        """
        if bench_name in self._anchor_cache:
            return self._anchor_cache[bench_name]

        # Handle explicit anchors first
        if bench_name in self.ANCHORS:
            return bench_name

        # Find the talent that unlocks this bench
        talent_name = self.item_to_talent.get(bench_name)
        if not talent_name:
            # Fallback for common benches that might be in the start or implicitly unlocked
            if bench_name in ["Campfire", "Firepit", "Drying_Rack", "PotBellyStove", 
                             "Cooking_Station", "Curing_Bench"]:
                return "Character" if bench_name in ["Campfire", "Firepit", "Drying_Rack"] else "Crafting_Bench"
            
            # If no talent exists for this bench name, default based on common prefixes
            if "T3_" in bench_name: return "Machine_Bench"
            if "T4_" in bench_name: return "Fabricator"
            return "Fabricator" # Safest default

        # Trace up the tree to find an anchor
        queue = deque([talent_name])
        visited = {talent_name}
        
        found_anchor = "Fabricator"
        best_tier = 5

        while queue:
            current = queue.popleft()
            
            if current in self.ANCHORS:
                tier = self.ANCHORS[current]
                if tier < best_tier:
                    best_tier = tier
                    found_anchor = current
                if best_tier == 1: break # Short circuit if we reached T1

            for parent in self.talent_parents.get(current, []):
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)

        # Final check: if we didn't find specific anchor but it's clearly T1 (no parents)
        if found_anchor == "Fabricator" and best_tier == 5:
            found_anchor = "Character"

        self._anchor_cache[bench_name] = found_anchor
        return found_anchor

    def get_bench_rank(self, bench_name: str) -> int:
        """
        Returns the numerical rank (1-4) for a given bench.
        """
        anchor = self._resolve_bench_anchor(bench_name)
        return self.ANCHORS.get(anchor, 4)

    def _get_talent_distance(self, anchor_name: str, target_talent: str) -> int:
        """
        Calculates distance in talent tree via BFS.
        """
        if anchor_name == target_talent:
            return 0
            
        queue = deque([(anchor_name, 0)])
        visited = {anchor_name}
        
        while queue:
            current, dist = queue.popleft()
            if current == target_talent:
                return dist
            
            for neighbor in self.talent_graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        
        return 1 # Fallback for T1 or missing paths
