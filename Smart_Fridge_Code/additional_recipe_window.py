from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QColor

# food_detection.py에 있는 FOOD_MAP을 여기에 복사해와야 합니다.
# 실제 프로젝트에서는 공통 모듈이나 설정 파일로 빼서 공유하는 것이 좋습니다.
FOOD_MAP = {
    "apple": ("apple", "🍎"), "banana": ("banana", "🍌"), "bell_pepper": ("bell_pepper", "🫑"),
    "cabage": ("cabage", "🥬"), "carrot": ("carrot", "🥕"), "chicken": ("chicken", "🍗"),
    "egg": ("egg", "🥚"), "fork": ("fork", "🍴"), "green": ("green", "🌿"),
    "milk": ("milk", "🥛"), "onion": ("onion", "🧅"), "potato": ("potato", "🥔")
}
# 재료 이름으로 이모티콘을 찾기 위한 역방향 맵 (없으면 빈 문자열)
INGREDIENT_EMOJI_MAP = {food_name: emoji for food_name, emoji in FOOD_MAP.values()}


class AdditionalRecipeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("추가 구매 시 가능한 레시피")
        self.setGeometry(400, 300, 800, 600) # 창 크기 조정

        main_layout = QVBoxLayout()

        self.title_label = QLabel("현재 재료 외 추가 구매 시 가능한 레시피:", self)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #0056b3;")
        main_layout.addWidget(self.title_label)

        self.info_label = QLabel("아래 레시피는 1-2개 재료만 더 구매하시면 만들 수 있습니다:", self)
        self.info_label.setStyleSheet("font-size: 14px; margin-bottom: 10px; color: #555;")
        main_layout.addWidget(self.info_label)

        # QTableWidget으로 변경
        self.recipe_table_widget = QTableWidget(0, 4, self) # 0행, 4열 (이모티콘, 레시피 이름, 보유 재료, 필요한 재료)
        self.recipe_table_widget.setHorizontalHeaderLabels(["", "레시피 이름", "보유 재료", "필요한 재료"])
        
        # 컬럼 너비 조정 (선택 사항)
        self.recipe_table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # 이모티콘
        self.recipe_table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # 레시피 이름
        self.recipe_table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # 보유 재료
        self.recipe_table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # 필요한 재료

        self.recipe_table_widget.verticalHeader().setVisible(False) # 행 번호 숨기기
        self.recipe_table_widget.setEditTriggers(QTableWidget.NoEditTriggers) # 편집 불가
        self.recipe_table_widget.setSelectionBehavior(QTableWidget.SelectRows) # 행 단위 선택

        self.recipe_table_widget.itemClicked.connect(self.open_recipe_url) # 셀 클릭 이벤트 연결
        self.recipe_table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.recipe_table_widget)

        self.setLayout(main_layout)

    def update_recipes(self, _, recipes):
        self.recipe_table_widget.clearContents() # 기존 내용 지우기
        self.recipe_table_widget.setRowCount(0) # 행 초기화

        if recipes:
            for row_idx, recipe in enumerate(recipes):
                self.recipe_table_widget.insertRow(row_idx)

                recipe_name = recipe.get('name', '이름 없음')
                required_ingredients = recipe.get('required_ingredients', [])
                optional_ingredients = recipe.get('optional_ingredients', [])
                missing_ingredients = recipe.get('missing_ingredients', [])

                # '보유 재료' 계산 (레시피에 필요한 재료 중 현재 부족하지 않은 것)
                # 이 로직은 `recipe_recommender.py`에서 `available_ingredients`를 받아와야 정확하지만,
                # 현재 전달되는 정보(recipe['required_ingredients']와 recipe['missing_ingredients'])만으로는
                # '레시피를 만들기 위해 필요한 재료 중 현재 보유하고 있는 재료'를 추정하는 방식으로 구성합니다.
                present_ingredients_for_recipe = sorted(list(set(required_ingredients) - set(missing_ingredients)))
                
                # 재료명에 이모티콘 추가
                present_str_with_emojis = []
                for ing in present_ingredients_for_recipe:
                    present_str_with_emojis.append(f"{INGREDIENT_EMOJI_MAP.get(ing, '')} {ing}")
                
                missing_str_with_emojis = []
                for ing in missing_ingredients:
                    missing_str_with_emojis.append(f"{INGREDIENT_EMOJI_MAP.get(ing, '')} {ing}")

                # 0열: 이모티콘 (레시피 아이콘은 없으므로 일단 첫 번째 필수 재료 아이콘 사용 또는 빈 칸)
                # 더 나은 아이콘이 있다면 여기를 수정하세요.
                first_req_ing = required_ingredients[0] if required_ingredients else ''
                emoji_item = QTableWidgetItem(INGREDIENT_EMOJI_MAP.get(first_req_ing, ''))
                emoji_item.setTextAlignment(Qt.AlignCenter)
                self.recipe_table_widget.setItem(row_idx, 0, emoji_item)

                # 1열: 레시피 이름
                name_item = QTableWidgetItem(recipe_name)
                name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.recipe_table_widget.setItem(row_idx, 1, name_item)

                # 2열: 보유 재료
                # 선택 재료도 여기에 포함하여 표시
                present_and_optional_display = []
                if present_str_with_emojis:
                    present_and_optional_display.extend(present_str_with_emojis)
                if optional_ingredients:
                    for opt_ing in optional_ingredients:
                         present_and_optional_display.append(f"{INGREDIENT_EMOJI_MAP.get(opt_ing, '')} {opt_ing} (선택)")

                present_item_text = ", ".join(present_and_optional_display) if present_and_optional_display else "없음"
                present_item = QTableWidgetItem(present_item_text)
                present_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.recipe_table_widget.setItem(row_idx, 2, present_item)

                # 3열: 필요한 재료
                missing_item_text = ", ".join(missing_str_with_emojis) if missing_str_with_emojis else "없음"
                missing_item = QTableWidgetItem(missing_item_text)
                missing_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.recipe_table_widget.setItem(row_idx, 3, missing_item)

                # 색상 강조
                color = QColor(0, 0, 0) # 기본 검은색
                if recipe.get('missing_count') == 1:
                    color = QColor(0, 120, 0) # 1개 부족 시 진한 녹색
                elif recipe.get('missing_count') == 2:
                    color = QColor(180, 80, 0) # 2개 부족 시 주황색

                for col in range(self.recipe_table_widget.columnCount()):
                    item = self.recipe_table_widget.item(row_idx, col)
                    if item:
                        item.setForeground(color)
                        # QTableWidgetItem에 실제 레시피 딕셔너리를 저장 (URL 열기용)
                        item.setData(Qt.UserRole, recipe) 
        else:
            # 레시피가 없을 경우 메시지 표시 (테이블 대신 QLabel을 쓰는 것이 더 깔끔할 수 있지만, 테이블에 표시)
            self.recipe_table_widget.setRowCount(1)
            no_recipe_item = QTableWidgetItem("현재 재료 외 추가 구매 시 가능한 레시피가 없습니다.")
            no_recipe_item.setTextAlignment(Qt.AlignCenter)
            self.recipe_table_widget.setSpan(0, 0, 1, 4) # 모든 컬럼에 걸쳐 메시지 표시
            self.recipe_table_widget.setItem(0, 0, no_recipe_item)

        self.recipe_table_widget.resizeRowsToContents() # 내용에 맞게 행 높이 조정
        self.recipe_table_widget.resizeColumnsToContents() # 내용에 맞게 열 너비 조정 (이모티콘 열에 유용)


    def open_recipe_url(self, item):
        # 클릭된 item에서 레시피 데이터 가져오기
        recipe = item.data(Qt.UserRole)
        
        if recipe:
            url = recipe.get("url")
            if url:
                QDesktopServices.openUrl(QUrl(url))
            else:
                print(f"URL이 없는 레시피: {recipe.get('name', '알 수 없는 레시피')}")
        else:
            print("클릭된 아이템에 레시피 데이터가 없습니다.")