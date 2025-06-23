from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QSizePolicy
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

class RecipeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recommended Recipe")
        self.setGeometry(300, 300, 700, 600)

        main_layout = QVBoxLayout()

        # --- Recipes available with current ingredients section ---
        self.title_label_now = QLabel("Recipes you can make with current ingredients:", self)
        self.title_label_now.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 5px; color: #333;")
        main_layout.addWidget(self.title_label_now)

        self.recipe_list_widget_now = QListWidget(self)
        self.recipe_list_widget_now.itemClicked.connect(self.open_recipe_url)
        self.recipe_list_widget_now.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.recipe_list_widget_now)

        self.setLayout(main_layout)

        # List to store all recipe data
        self.all_recipes_data = [] 

    def update_recipes(self, recommendations):
        self.recipe_list_widget_now.clear()
        self.all_recipes_data = []

        can_make_now = recommendations.get("can_make_now", [])

        # Add recipes that can be made with current ingredients
        if can_make_now:
            for recipe in can_make_now:
                ingredients_text = f"Required: {', '.join(recipe.get('required_ingredients', []))}"
                if recipe.get('optional_ingredients'):
                    ingredients_text += f" | Optional: {', '.join(recipe['optional_ingredients'])}"
                
                item_text = f"• {recipe['name']} ({ingredients_text})"
                list_item = QListWidgetItem(item_text)
                self.recipe_list_widget_now.addItem(list_item)
                list_item.setData(Qt.UserRole, recipe)
        else:
            list_item = QListWidgetItem("No recipes can be made with your current ingredients.")
            self.recipe_list_widget_now.addItem(list_item)

    def open_recipe_url(self, item):
        recipe = item.data(Qt.UserRole) 
        
        if recipe: # If valid recipe data exists
            url = recipe.get("url")
            if url:
                QDesktopServices.openUrl(QUrl(url))
            else:
                print(f"Recipe has no URL: {recipe.get('name', 'Unknown Recipe')}")
        else:
            print("Clicked item has no recipe data.")
