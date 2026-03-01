from abc import ABC, abstractmethod
from typing import List
from icarus_consumables.models.consumable import ConsumableData
from icarus_consumables.utils.path_resolver import resolve_path

class BaseGenerator(ABC):
    """Abstract base class for all output generators."""

    def __init__(self, filename: str):
        self.output_path = resolve_path(f"output/{filename}")
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def generate(self, data: List[ConsumableData]) -> None:
        """Generates the output file from the provided data."""
        pass

    def _format_stats(self, consumable: ConsumableData) -> str:
        """Helper to format stats into a readable string."""
        parts = []
        for name, val in consumable.base_stats.items():
            parts.append(f"{name}: {val:+g}")
        return ", ".join(parts)
