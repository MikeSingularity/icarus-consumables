from dataclasses import dataclass

@dataclass
class TierInfo:
    """
    Metadata describing the technological standing of an item.
    Combines the discrete game tier (1-4) with a fractional offset 
    representing its depth within that tier's talent tree.

    Example:
        >>> tier = TierInfo(
        ...     base_tier=2,
        ...     fractional_offset=0.3,
        ...     total_tier=2.3,
        ...     anchor_bench="Crafting_Bench",
        ...     is_harvested=False
        ... )
    """
    base_tier: int            # Integer anchor (1-4)
    fractional_offset: float  # Talent tree depth (0.0 - 0.9)
    total_tier: float         # The effective tier (e.g., 2.3)
    anchor_bench: str         # The primary bench for the tier (e.g., "Crafting_Bench")
    is_harvested: bool        # True if Tier 0 (not crafted)
    is_orbital: bool = False  # True if purchased from orbit
