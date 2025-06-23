from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QColor


FOOD_MAP = {
    "apple": ("apple", "🍎"), "banana": ("banana", "🍌"), "bell_pepper": ("bell_pepper", "🫑"),
    "cabage": ("cabage", "🥬"), "carrot": ("carrot", "🥕"), "chicken": ("chicken", "🍗"),
    "egg": ("egg", "🥚"), "fork": ("fork", "🍴"), "green": ("green", "🌿"),
    "milk": ("milk", "🥛"), "onion": ("onion", "🧅"), "potato": ("potato", "🥔")
}
# Reverse map to find emoji by ingredient name (empty string if not found)
INGREDIENT_EMOJI_MAP = {food_name: emoji for food_name, emoji in FOOD_MAP.values()}


class AdditionalRecipeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recipes with Additional Purchase")
        self.setGeometry(400, 300, 800, 600) # Adjust window size

        main_layout = QVBoxLayout()

        self.title_label = QLabel("Recipes Available with Additional Purchases:", self)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #0056b3;")
        main_layout.addWidget(self.title_label)

        self.info_label = QLabel("The recipes below can be made by purchasing just 1-2 more ingredients:", self)
        self.info_label.setStyleSheet("font-size: 14px; margin-bottom: 10px; color: #555;")
        main_layout.addWidget(self.info_label)

        # Changed to QTableWidget
        self.recipe_table_widget = QTableWidget(0, 4, self) # 0 rows, 4 columns (Emoji, Recipe Name, Owned Ingredients, Needed Ingredients)
        self.recipe_table_widget.setHorizontalHeaderLabels(["", "Recipe Name", "Owned Ingredients", "Needed Ingredients"])
        
        # Adjust column widths (optional)
        self.recipe_table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # Emoji
        self.recipe_table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Recipe Name
        self.recipe_table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # Owned Ingredients
        self.recipe_table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # Needed Ingredients

        self.recipe_table_widget.verticalHeader().setVisible(False) # Hide row numbers
        self.recipe_table_widget.setEditTriggers(QTableWidget.NoEditTriggers) # Disable editing
        self.recipe_table_widget.setSelectionBehavior(QTableWidget.SelectRows) # Select entire rows

        self.recipe_table_widget.itemClicked.connect(self.open_recipe_url) # Connect cell click event
        self.recipe_table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.recipe_table_widget)

        self.setLayout(main_layout)

    def update_recipes(self, _, recipes):
        self.recipe_table_widget.clearContents() # Clear existing content
        self.recipe_table_widget.setRowCount(0) # Reset row count

        if recipes:
            for row_idx, recipe in enumerate(recipes):
                self.recipe_table_widget.insertRow(row_idx)

                recipe_name = recipe.get('name', 'Unnamed')
                required_ingredients = recipe.get('required_ingredients', [])
                optional_ingredients = recipe.get('optional_ingredients', [])
                missing_ingredients = recipe.get('missing_ingredients', [])

                # Calculate 'Owned Ingredients' (ingredients required for the recipe that are not currently missing)
                present_ingredients_for_recipe = sorted(list(set(required_ingredients) - set(missing_ingredients)))
                
                # Add emojis to ingredient names
                present_str_with_emojis = []
                for ing in present_ingredients_for_recipe:
                    present_str_with_emojis.append(f"{INGREDIENT_EMOJI_MAP.get(ing, '')} {ing}")
                
                missing_str_with_emojis = []
                for ing in missing_ingredients:
                    missing_str_with_emojis.append(f"{INGREDIENT_EMOJI_MAP.get(ing, '')} {ing}")

                first_req_ing = required_ingredients[0] if required_ingredients else ''
                emoji_item = QTableWidgetItem(INGREDIENT_EMOJI_MAP.get(first_req_ing, ''))
                emoji_item.setTextAlignment(Qt.AlignCenter)
                self.recipe_table_widget.setItem(row_idx, 0, emoji_item)

                # Column 1: Recipe Name
                name_item = QTableWidgetItem(recipe_name)
                name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.recipe_table_widget.setItem(row_idx, 1, name_item)

                # Column 2: Owned Ingredients
                # Include optional ingredients here for display
                present_and_optional_display = []
                if present_str_with_emojis:
                    present_and_optional_display.extend(present_str_with_emojis)
                if optional_ingredients:
                    for opt_ing in optional_ingredients:
                        present_and_optional_display.append(f"{INGREDIENT_EMOJI_MAP.get(opt_ing, '')} {opt_ing} (Optional)")

                present_item_text = ", ".join(present_and_optional_display) if present_and_optional_display else "None"
                present_item = QTableWidgetItem(present_item_text)
                present_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.recipe_table_widget.setItem(row_idx, 2, present_item)

                # Column 3: Needed Ingredients
                missing_item_text = ", ".join(missing_str_with_emojis) if missing_str_with_emojis else "None"
                missing_item = QTableWidgetItem(missing_item_text)
                missing_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.recipe_table_widget.setItem(row_idx, 3, missing_item)

                color = QColor(0, 0, 0) # Default color (black)
                if recipe.get('missing_count') == 1:
                    color = QColor(0, 120, 0) # Green for 1 missing
                elif recipe.get('missing_count') == 2:
                    color = QColor(180, 80, 0) # Orange for 2 missing

                for col in range(self.recipe_table_widget.columnCount()):
                    item = self.recipe_table_widget.item(row_idx, col)
                    if item:
                        item.setForeground(color)
                        item.setData(Qt.UserRole, recipe) # Store recipe data with the item
        else:
            # Display message if no recipes are available
            self.recipe_table_widget.setRowCount(1)
            no_recipe_item = QTableWidgetItem("No recipes available with additional purchases.")
            no_recipe_item.setTextAlignment(Qt.AlignCenter)
            self.recipe_table_widget.setSpan(0, 0, 1, 4) # Span across all columns
            self.recipe_table_widget.setItem(0, 0, no_recipe_item)

        self.recipe_table_widget.resizeRowsToContents()
        self.recipe_table_widget.resizeColumnsToContents()


    def open_recipe_url(self, item):
        # Retrieve recipe data from the clicked item
        recipe = item.data(Qt.UserRole)
        
        if recipe:
            url = recipe.get("url")
            if url:
                QDesktopServices.openUrl(QUrl(url))
            else:
                print(f"Recipe has no URL: {recipe.get('name', 'Unknown Recipe')}")
        else:
            print("Clicked item has no recipe data.")
