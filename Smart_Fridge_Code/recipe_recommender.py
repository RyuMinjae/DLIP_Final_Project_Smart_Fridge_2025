import json

class RecipeRecommender:
    def __init__(self, recipes_file):
        self.recipes = self._load_recipes(recipes_file)

    def _load_recipes(self, recipes_file):
        try:
            with open(recipes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: 레시피 파일 '{recipes_file}'을 찾을 수 없습니다.")
            return []
        except json.JSONDecodeError:
            print(f"Error: '{recipes_file}'에서 JSON을 디코딩할 수 없습니다.")
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

    # 이 함수의 정의를 아래와 같이 변경해야 합니다!
    def get_recommendations_with_missing(self, available_ingredients): # 'available_ingredients'만 받도록 변경
        # available_ingredients는 현재 냉장고에 있는 모든 재료 (클릭된 재료 포함)
        
        can_make_with_purchase = []
        available_ingredients_lower = {ing.lower() for ing in available_ingredients}

        for recipe in self.recipes:
            recipe_name = recipe.get("name")
            required_ingredients = {ing.lower() for ing in recipe.get("required_ingredients", [])}
            optional_ingredients = {ing.lower() for ing in recipe.get("optional_ingredients", [])}
            recipe_url = recipe.get("url")

            # 현재 보유 재료와 필수 재료를 비교하여 부족한 재료를 찾습니다.
            missing_required = required_ingredients - available_ingredients_lower
            
            # 부족한 필수 재료가 1개 또는 2개인 레시피를 찾습니다.
            if 1 <= len(missing_required) <= 2:
                can_make_with_purchase.append({
                    "name": recipe_name,
                    "required_ingredients": list(required_ingredients),
                    "optional_ingredients": list(optional_ingredients),
                    "url": recipe_url,
                    "missing_count": len(missing_required),
                    "missing_ingredients": list(missing_required) # 어떤 재료가 부족한지 명시
                })
        
        return can_make_with_purchase