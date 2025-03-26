import json
import math

INPUT_FILE = "recipes.jsonl"
OUTPUT_FILE = "chunks.jsonl"

def convert_to_minutes(time_str):
    # Input examples: PT24H20M, PT25M, PT4H, PT0S
    try:
        if not time_str:
            return 0
        if time_str == "nan" or (isinstance(time_str, float) and math.isnan(time_str)):
            return 0
        elif "H" in time_str and "M" in time_str:
            hours, minutes = time_str.split("H")
            minutes = minutes.replace("M", "")
            return int(hours.replace("PT", "")) * 60 + int(minutes)
        elif "H" in time_str:
            return int(time_str.replace("PT", "").replace("H", "")) * 60
        else:
            return int(time_str.replace("PT", "").replace("M", ""))
    except Exception as e:
        if time_str == "PT0S":
            return 0
        print (e)
        print(f"Error converting time string: {time_str}")

def split_to_arr(value):
    return value.replace("c(", "").replace(")", "").replace("\"", "").split(", ")

with open(INPUT_FILE, "r", encoding="utf-8") as infile, open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    for linenum, line in enumerate(infile):
        recipe = json.loads(line)
        recipe_title = recipe.get("Name", "")
        recipe_ingredients = split_to_arr(recipe.get("RecipeIngredientParts", ""))
        recipe_instructions = split_to_arr(recipe.get("RecipeInstructions", ""))
        
        text = f"""
            {recipe_title}
            Ingredients: {", ".join(recipe_ingredients)}
            Instructions: {", ".join(recipe_instructions)}
        """
            
        chunk_entry = {
            "Id": recipe.get("RecipeId", ""),
            "Name": recipe_title,
            "DatePublished": recipe.get("DatePublished", ""),
            "AuthorName": recipe.get("AuthorName", ""),
            "PrepTime": convert_to_minutes(recipe.get("PrepTime", "")),
            "CookTime": convert_to_minutes(recipe.get("CookTime", "")),
            "RecipeCategory": recipe.get("RecipeCategory", ""),
            "Ingredients": recipe_ingredients,
            "RecipeInstructions": recipe_instructions,
            "Text": text
        }
        outfile.write(json.dumps(chunk_entry) + "\n")
            
        if linenum > 0 and linenum % 1000 == 0:
            print(f"Chunking progress: {linenum} lines processed so far...")

print(f"Chunking complete. Output saved to {OUTPUT_FILE}")
