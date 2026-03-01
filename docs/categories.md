# Item Categories

# Animal Food
If an item provides a BaseFoodRecovery value and has "Animal" or "Omni" in the name, it is AnimalFood, else

# Food
If an item provides a BaseFoodRecovery value, it is a Food item, else

# Drink
If an item provides a BaseWaterRecovery value or starts with "Drink_", it is a Drink item, else

# Workshop
If an item id includes a string in the list ['_Ammo', '_Arrow', 'Biolab_', '_Bolt', '_Resource_Pack'] OR is an Orbital item (bought with currency), it is a Workshop item, else

# Medicine
An item is a Medicine item
