import argparse
import sys
import json
from icarus_food.services.data_loader import IcarusDataLoader
from icarus_food.parser import IcarusFoodParserApp
from icarus_food.generators.json import JsonGenerator
from icarus_food.utils.path_resolver import resolve_path

def main():
    """Main entry point for the Icarus Food Parser."""
    parser = argparse.ArgumentParser(description="Icarus Food and Consumable Data Parser")
    parser.add_argument(
        "--data-dir", 
        type=str, 
        default="unpacked_icarus_data",
        help="Path to the directory containing unpacked Icarus game data (JSON files)"
    )
    args = parser.parse_args()

    try:
        # 1. Load configuration
        config_path = resolve_path("src/icarus_food/config/processing_config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 2. Initialize data loader
        loader = IcarusDataLoader(pak_dir=args.data_dir)
        
        # 3. Create app instance
        app = IcarusFoodParserApp(loader, config)
        
        # 4. Register generators
        app.add_generator(JsonGenerator(
            "consumables_data.json", 
            parser_version=config.get("PARSER_VERSION", "v2.1.0"),
            game_version=config.get("GAME_VERSION", "TBD")
        ))
        
        # 5. Run pipeline
        app.run()
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
