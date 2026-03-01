from icarus_consumables.services.data_loader import IcarusDataLoader
from icarus_consumables.services.translation import IcarusTranslationService

def main():
    loader = IcarusDataLoader()
    data = loader.load_all_data()
    itemable_rows = data.get("itemable", [])
    translator = IcarusTranslationService(itemable_rows)
    
    test_names = [
        "Raw_Meat", "Corn", "Seed", "Squash", "Pumpkin", "Potato", "Bean", "Mushroom", "Carrot",
        "Campfire", "Firepit", "Kitchen_Stove"
    ]
    
    for name in test_names:
        display = translator.get_display_name(name)
        print(f"'{name}' -> '{display}'")

if __name__ == "__main__":
    main()
