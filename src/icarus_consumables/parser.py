from icarus_consumables.services.data_loader import IcarusDataLoader
from icarus_consumables.services.translation import IcarusTranslationService
from icarus_consumables.services.tier_mapper import IcarusTierMapper
from icarus_consumables.services.recipe_service import RecipeService
from icarus_consumables.services.modifier_service import ModifierService
from icarus_consumables.services.consumable_parser import ConsumableDataParser
from icarus_consumables.services.category_service import CategoryService
from icarus_consumables.services.override_service import OverrideService
from icarus_consumables.services.farming_service import FarmingService
from icarus_consumables.services.tag_service import IcarusTagService
from icarus_consumables.generators.base import BaseGenerator
from typing import Any

class IcarusFoodParserApp:
    """
    The main orchestration class for the food parser application.
    """

    def __init__(self, data_loader: IcarusDataLoader, config: dict[str, Any]):
        """
        Initializes the application with a data loader and configuration.
        """

        self.data_loader = data_loader
        self.config = config
        self.generators: list[BaseGenerator] = []

    def add_generator(self, generator: BaseGenerator):
        """
        Adds an output generator to the pipeline.
        """
        self.generators.append(generator)

    def run(self):
        """
        Executes the full parsing and generation pipeline.
        """
        print("🚀 Starting Icarus Food Data Refactor (v2)...")
        
        # 1. Load Data
        print("📂 Loading game data files...")
        data = self.data_loader.load_all_data()
        
        translation_service = IcarusTranslationService(data["itemable"], data["items_static"])

        # Build Master Item Index
        from icarus_consumables.services.item_index import ItemIndexService
        print("🛠 Building Master Item Index...")
        item_index = ItemIndexService()
        for row in data["items_static"]:
            item_index.add_entry("D_ItemsStatic", str(row.get("Name")))
        for row in data["consumables"]:
            item_index.add_entry("D_Consumable", str(row.get("Name")))
        for row in data["item_templates"]:
            item_index.add_entry("D_ItemTemplate", str(row.get("Name")))
        for row in data["workshop_items"]:
            item_index.add_entry("D_WorkshopItems", str(row.get("Name")))

        # 2. Initialize Services
        print("🛠 Initializing services...")
        tag_service = IcarusTagService(data["crafting_tags"], data["tag_queries"])
        recipe_service = RecipeService(data["recipes"], data["items_static"], tag_service, item_index)
        
        # Build Item Map for TierMapper (Systematic tag lookup)
        static_item_dict = {str(r.get("Name")): r for r in data["items_static"]}
        tier_mapper = IcarusTierMapper(
            static_item_dict, 
            data["talents"], 
            recipe_service, 
            data["workshop_items"],
            data["item_templates"],
            data["consumables"],
            item_index
        )
        
        modifier_service = ModifierService(data["modifiers"])
        category_service = CategoryService(self.config)
        override_service = OverrideService(self.config.get("OVERRIDES_DIR", "data/overrides"))
        farming_service = FarmingService(data["farming_seeds"], data["farming_growth_states"], data["item_rewards"])
        
        # 3. Parse Items
        print("🔍 Parsing consumables...")
        self.consumable_parser = ConsumableDataParser(
            translation_service,
            recipe_service,
            tier_mapper,
            modifier_service,
            category_service,
            override_service,
            farming_service,
            item_index,
            data["decayable"]
        )
        
        processed_data = self.consumable_parser.parse_all(data["consumables"], data["itemable"], data["items_static"], data["decayable"])
        print(f"✅ Processed {len(processed_data)} items.")
        
        # 4. Generate Output
        print("📝 Generating output files...")
        item_index.export_to_json("output/item_index_mapping.json")
        for gen in self.generators:
            print(f"   - Generating {gen.output_path.name}...")
            gen.generate(processed_data)
            
        print("✨ Refactor pipeline complete!")
