from typing import Any, Optional
from dataclasses import dataclass

@dataclass
class GrowthInfo:
    time_seconds: int
    yield_min: int
    yield_max: int

class FarmingService:
    """
    Handles lookup and calculation of crop growth data.
    """
    def __init__(
        self, 
        seeds_rows: list[dict[str, Any]], 
        growth_states_rows: list[dict[str, Any]], 
        rewards_rows: list[dict[str, Any]]
    ):
        self.growth_states = {row["Name"]: row for row in growth_states_rows}
        self.rewards = {row["Name"]: row for row in rewards_rows}
        self.crop_map: dict[str, GrowthInfo] = {}
        self._initialize_crop_map(seeds_rows)

    def _initialize_crop_map(self, seeds_rows: list[dict[str, Any]]):
        """
        Builds a map from the resulting food item to its growth info.
        """
        for seed in seeds_rows:
            crop_reward_id = seed.get("CropRewards", {}).get("RowName")
            if not crop_reward_id or crop_reward_id == "None":
                continue

            # Calculate Growth Time (Stages 1-4)
            total_time = 0
            for stage_key in ["Stage1", "Stage2", "Stage3", "Stage4"]:
                state_id = seed.get(stage_key, {}).get("RowName")
                if state_id and state_id in self.growth_states:
                    total_time += self.growth_states[state_id].get("TimeToNextState", 0)

            # Find harvest yield from rewards
            reward_entry = self.rewards.get(crop_reward_id)
            if reward_entry:
                for reward in reward_entry.get("Rewards", []):
                    item_name = reward.get("Item", {}).get("RowName")
                    if not item_name:
                        continue
                    
                    # We map this growth info to the primary item produced
                    # (Note: Some crops produce multiple items like Fiber+Seeds, 
                    # we focus on the main food/material)
                    if item_name not in self.crop_map or reward.get("MinRandomStackCount", 0) > self.crop_map[item_name].yield_min:
                        self.crop_map[item_name] = GrowthInfo(
                            time_seconds=total_time,
                            yield_min=reward.get("MinRandomStackCount", 0),
                            yield_max=reward.get("MaxRandomStackCount", 0)
                        )

    def get_growth_info(self, item_name: str) -> Optional[GrowthInfo]:
        """
        Returns growth info for a specific item name (e.g., 'Berry', 'Carrot').
        """
        return self.crop_map.get(item_name)
