import json
import re

# Define crafting bench tiers based on actual data from recipes
CRAFTING_BENCH_TIERS = {
    # Tier 0: Handcrafted or gathered (no specific crafting bench)
    0: ["None"],
    
    # Tier 1: Basic cooking and crafting
    1: ["Campfire", "Firepit", "Character", "Drying_Rack"],
    
    # Tier 2: Intermediate cooking and crafting
    2: ["PotBellyStove", "Cooking_Station", "T3_Smoker"],
    
    # Tier 3: Advanced cooking and crafting
    3: ["Kitchen_Stove", "Kitchen_Bench", "T4_Smoker", "Seed_Extractor"],
    
    # Tier 4: High-end cooking and crafting
    4: ["Electric_Stove", "Advanced_Kitchen_Bench", "Butchery_Bench", "Herbalism_Bench", "Animal_Bench", "Machining_Bench", "Fabricator", "Manufacturer", "Carpentry_Bench", "Carpentry_Bench_T4", "Masonry_Bench", "Masonry_Bench_T3", "Masonry_Bench_T4", "Cement_Mixer", "Glassworking_Bench"]
}

def get_tier_from_recipe_sets(recipe_sets):
    if not recipe_sets:
        return "0"
    
    lowest_tier = 4
    for tier, benches in CRAFTING_BENCH_TIERS.items():
        for bench in benches:
            if any(bench == recipe_set for recipe_set in recipe_sets):
                if tier < lowest_tier:
                    lowest_tier = tier
    
    return str(lowest_tier)

def test_tier_assignment():
    # Test with various recipe sets
    test_recipe_sets = [
        ["Kitchen_Stove", "Electric_Stove"],
        ["Campfire", "Firepit", "PotBellyStove"],
        ["Advanced_Kitchen_Bench"],
        ["Character"],
        ["Cooking_Station", "Kitchen_Bench"]
    ]
    
    print("Testing tier assignment:")
    print("-" * 50)
    
    for sets in test_recipe_sets:
        tier = get_tier_from_recipe_sets(sets)
        print(f"Recipe Sets: {sets}")
        print(f"Tier: {tier}")
        print()
    
    print("CRAFTING_BENCH_TIERS:")
    print("-" * 50)
    for tier, benches in CRAFTING_BENCH_TIERS.items():
        print(f"Tier {tier}: {benches}")

if __name__ == "__main__":
    test_tier_assignment()