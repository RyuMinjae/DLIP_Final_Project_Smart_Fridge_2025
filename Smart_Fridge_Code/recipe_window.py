from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QSizePolicy
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

class RecipeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🍲 추천 레시피")
        self.setGeometry(300, 300, 700, 600) # 창 크기 확장

        main_layout = QVBoxLayout()

        # --- 현재 재료로 가능한 레시피 섹션 ---
        self.title_label_now = QLabel("✨ 현재 재료로 만들 수 있는 레시피:", self)
        self.title_label_now.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 5px; color: #333;")
        main_layout.addWidget(self.title_label_now)

        self.recipe_list_widget_now = QListWidget(self)
        self.recipe_list_widget_now.itemClicked.connect(self.open_recipe_url)
        self.recipe_list_widget_now.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # 확장 정책
        main_layout.addWidget(self.recipe_list_widget_now)

        self.setLayout(main_layout)

        # 모든 레시피 데이터를 저장할 리스트 (인덱스 관리를 위해 통합)
        self.all_recipes_data = [] 

    def update_recipes(self, recommendations):
        self.recipe_list_widget_now.clear()
        # self.recipe_list_widget_purchase.clear()  <-- 이 줄을 제거하거나 주석 처리해야 합니다.
        self.all_recipes_data = [] # 데이터 초기화

        can_make_now = recommendations.get("can_make_now", [])
        # can_make_with_purchase = recommendations.get("can_make_with_purchase", []) # 이 변수는 더 이상 사용되지 않습니다.

        # 현재 재료로 가능한 레시피 추가
        if can_make_now:
            for recipe in can_make_now:
                ingredients_text = f"필수: {', '.join(recipe.get('required_ingredients', []))}"
                if recipe.get('optional_ingredients'):
                    ingredients_text += f" | 선택: {', '.join(recipe['optional_ingredients'])}"
                
                item_text = f"• {recipe['name']} ({ingredients_text})"
                list_item = QListWidgetItem(item_text)
                self.recipe_list_widget_now.addItem(list_item)
                # Note: self.all_recipes_data는 이전에 두 리스트를 합치기 위해 사용되었으나,
                # 현재는 하나의 리스트만 있으므로 필요에 따라 사용 방식을 조정할 수 있습니다.
                # 단순화된 open_recipe_url을 위해 Qt.UserRole에 직접 데이터를 저장하는 방식이 더 효율적입니다.
                list_item.setData(Qt.UserRole, recipe) # 레시피 딕셔너리 전체를 저장
        else:
            list_item = QListWidgetItem("현재 재료로 만들 수 있는 레시피가 없습니다.")
            self.recipe_list_widget_now.addItem(list_item)

    def open_recipe_url(self, item):
        # item에서 직접 데이터 가져오기 (update_recipes에서 set해준 데이터)
        recipe = item.data(Qt.UserRole) 
        
        if recipe: # 유효한 레시피 데이터가 있을 경우
            url = recipe.get("url")
            if url:
                QDesktopServices.openUrl(QUrl(url))
            else:
                print(f"URL이 없는 레시피: {recipe.get('name', '알 수 없는 레시피')}")
        else:
            print("클릭된 아이템에 레시피 데이터가 없습니다.")