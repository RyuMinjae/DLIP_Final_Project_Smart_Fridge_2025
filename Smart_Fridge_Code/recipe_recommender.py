import json

class RecipeRecommender:
    def __init__(self, recipes_file):
        self.recipes = self._load_recipes(recipes_file)

    def _load_recipes(self, recipes_file):
        try:
            with open(recipes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Recipe file '{recipes_file}' not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{recipes_file}'.")
            return []

    def get_recommendations(self, available_ingredients):
        can_make_now = []
        can_make_with_purchase = []

        available_ingredients_lower = {ing.lower() for ing in available_ingredients}

        for recipe in self.recipes:
            recipe_name = recipe.get("name")
            required_ingredients = {ing.lower() for ing in recipe.get("required_ingredients", [])}
            optional_ingredients = {ing.lower() for ing in recipe.get("optional_ingredients", [])}
            recipe_url = recipe.get("url")

            missing_required = required_ingredients - available_ingredients_lower
            
            if not missing_required:
                can_make_now.append({
                    "name": recipe_name,
                    "required_ingredients": list(required_ingredients),
                    "optional_ingredients": list(optional_ingredients),
                    "url": recipe_url,
                    "missing_count": 0,
                    "missing_ingredients": []
                })
            elif 1 <= len(missing_required) <= 2:
                can_make_with_purchase.append({
                    "name": recipe_name,
                    "required_ingredients": list(required_ingredients),
                    "optional_ingredients": list(optional_ingredients),
                    "url": recipe_url,
                    "missing_count": len(missing_required),
                    "missing_ingredients": list(missing_required)
                })
        
        return {
            "can_make_now": can_make_now,
            "can_make_with_purchase": can_make_with_purchase
        }

    def get_recommendations_with_missing(self, available_ingredients):
        can_make_with_purchase = []
        available_ingredients_lower = {ing.lower() for ing in available_ingredients}

        for recipe in self.recipes:
            recipe_name = recipe.get("name")
            required_ingredients = {ing.lower() for ing in recipe.get("required_ingredients", [])}
            optional_ingredients = {ing.lower() for ing in recipe.get("optional_ingredients", [])}
            recipe_url = recipe.get("url")

            # Compares current available ingredients with required ingredients to find missing ones.
            missing_required = required_ingredients - available_ingredients_lower
            
            # Finds recipes that are missing 1 or 2 required ingredients.
            if 1 <= len(missing_required) <= 2:
                can_make_with_purchase.append({
                    "name": recipe_name,
                    "required_ingredients": list(required_ingredients),
                    "optional_ingredients": list(optional_ingredients),
                    "url": recipe_url,
                    "missing_count": len(missing_required),
                    "missing_ingredients": list(missing_required) # Specifies which ingredients are missing.
                })
        
        return can_make_with_purchase
