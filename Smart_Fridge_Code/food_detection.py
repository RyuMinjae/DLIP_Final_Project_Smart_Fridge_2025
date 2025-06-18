import cv2
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QPushButton
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor

from ultralytics import YOLO
import sys
from recipe_recommender import RecipeRecommender
from recipe_window import RecipeWindow
from additional_recipe_window import AdditionalRecipeWindow

# 음식 감지 정보
FOOD = {
    "apple": ["", 0, None], 
    "banana": ["", 0, None], 
    "bell_pepper": ["", 0, None],
    "cabage": ["", 0, None], 
    "carrot": ["", 0, None], "chicken": ["", 0, None],
    "egg": ["", 0, None], "fork": ["", 0, None], "green": ["", 0, None],
    "milk": ["", 0, None], "onion": ["", 0, None], "potato": ["", 0, None]
}

FOOD_MAP = {
    "apple": ("apple", "🍎"), "banana": ("banana", "🍌"), "bell_pepper": ("bell_pepper", "🫑"),
    "cabage": ("cabage", "🥬"), "carrot": ("carrot", "🥕"), "chicken": ("chicken", "🍗"),
    "egg": ("egg", "🥚"), "fork": ("fork", "🍴"), "green": ("green", "🌿"),
    "milk": ("milk", "🥛"), "onion": ("onion", "🧅"), "potato": ("potato", "🥔")
}


class MainWindow(QMainWindow):
    def __init__(self, model_path="best.pt"):
        super().__init__()
        self.setWindowTitle("Smart Refrigerator")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()
        self.label = QLabel("Smart Refrigerator", self)
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.label)

        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels([" ", "이름", "등록 시간", "경과 시간"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.table)

        # 테이블 아이템 클릭 이벤트 연결
        self.table.cellClicked.connect(self.on_table_cell_clicked)

        self.recommend_button = QPushButton("현재 재료 레시피 추천받기", self)
        self.recommend_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;"
        )
        self.recommend_button.clicked.connect(self.show_recipe_recommendations)
        layout.addWidget(self.recommend_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.model = YOLO(model_path)
        self.recipe_recommender = RecipeRecommender("recipes.json")

        self.cap = cv2.VideoCapture("DLIP_Test_Video_Simple2.mp4")
        if not self.cap.isOpened():
            QMessageBox.critical(self, "에러", "비디오 파일을 열 수 없습니다.")
            sys.exit()

        self.timer = QTimer()
        self.timer.timeout.connect(self.detect_from_camera)
        self.timer.start(100)

        self.recipe_window = None
        self.additional_recipe_window = None # 추가 레시피 창 인스턴스 초기화

    def detect_from_camera(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.cap.release()
            cv2.destroyAllWindows()
            return

        results = self.model(frame)
        boxes = results[0].boxes
        class_names = self.model.names

        now = datetime.now()
        detected_now = set()

        for i in range(len(boxes)):
            conf = boxes.conf[i].item()
            if conf < 0.5:
                continue

            cls_id = int(boxes.cls[i])
            cls_name = class_names[cls_id]

            if cls_name in FOOD_MAP:
                food_name, emote = FOOD_MAP[cls_name]
                detected_now.add(food_name)
                DOW, SP_delta = self.update_food_info(food_name, now)
                self.update_ui(food_name, emote, DOW, SP_delta)

            xyxy = boxes.xyxy[i].tolist()
            x1, y1, x2, y2 = map(int, xyxy)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{cls_name} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        for food in list(FOOD.keys()):
            if FOOD[food][1] == 1 and food not in detected_now:
                FOOD[food][1] = 0
                FOOD[food][0] = ""
                FOOD[food][2] = None
                self.remove_from_ui(food)
            elif FOOD[food][1] == 1:
                DOW, SP_delta = self.update_food_info(food, now)
                self.update_ui(food, FOOD_MAP[food][1], DOW, SP_delta)

        cv2.imshow("Webcam Detection", cv2.resize(frame, (900, 650)))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.close()

    def update_food_info(self, food_name, current_time):
        now_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        if FOOD[food_name][1] == 0:
            FOOD[food_name][1] = 1
            FOOD[food_name][0] = now_str
            FOOD[food_name][2] = current_time
            SP = "0:00:00"
        else:
            start_time = FOOD[food_name][2]
            if start_time:
                SP_delta = current_time - start_time
                SP = str(SP_delta).split('.')[0]
            else:
                SP = "오류"
        return FOOD[food_name][0], SP

    def update_ui(self, food_name, emote, DOW, SP):
        row = self.find_row(food_name)
        if row == -1:
            row = self.table.rowCount()
            self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(emote))
        self.table.setItem(row, 1, QTableWidgetItem(food_name))
        self.table.setItem(row, 2, QTableWidgetItem(DOW))
        self.table.setItem(row, 3, QTableWidgetItem(SP))

        try:
            start_time = FOOD[food_name][2]
            if start_time:
                elapsed_seconds = (datetime.now() - start_time).total_seconds()
            else:
                elapsed_seconds = 0
        except Exception:
            elapsed_seconds = 0

        for col in range(4):
            item = self.table.item(row, col)
            if item:
                item.setTextAlignment(Qt.AlignCenter)
                if elapsed_seconds >= 10:
                    item.setForeground(QColor(255, 0, 0))
                else:
                    item.setForeground(QColor(0, 0, 0))

    def remove_from_ui(self, food_name):
        row = self.find_row(food_name)
        if row != -1:
            self.table.removeRow(row)

    def find_row(self, food_name):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item and item.text() == food_name:
                return row
        return -1

    def show_recipe_recommendations(self):
        current_ingredients = [food for food, info in FOOD.items() if info[1] == 1]
        
        recommended_recipes_data = self.recipe_recommender.get_recommendations(current_ingredients)

        if not self.recipe_window:
            self.recipe_window = RecipeWindow()

        # RecipeWindow의 update_recipes 함수에 딕셔너리 데이터 전달
        self.recipe_window.update_recipes(recommended_recipes_data)
        self.recipe_window.show()

    # 테이블 셀 클릭 이벤트 핸들러 수정
    def on_table_cell_clicked(self, row, column):
        # '이름' 컬럼 (인덱스 1)이 클릭되었을 때만 처리
        if column == 1:
            item = self.table.item(row, column)
            if item:
                # 클릭된 재료를 포함하여 현재 냉장고에 있는 모든 재료를 가져옵니다.
                all_current_ingredients = [food for food, info in FOOD.items() if info[1] == 1]
                
                # '추가 구매 시 가능한 레시피' 추천 로직 호출
                # 이 함수는 "현재 보유 재료 외에 1-2개 추가 구매 시" 가능한 레시피를 찾습니다.
                self.show_additional_recipe_recommendations(all_current_ingredients)

    def show_additional_recipe_recommendations(self, current_available_ingredients):
        # recipe_recommender의 get_recommendations_with_missing 함수는 이제
        # "current_available_ingredients"를 가지고 있는 상태에서
        # 1-2개 재료만 더 구매하면 만들 수 있는 레시피를 찾습니다.
        additional_recommended_recipes = self.recipe_recommender.get_recommendations_with_missing(
            current_available_ingredients
        )
        
        if not self.additional_recipe_window:
            self.additional_recipe_window = AdditionalRecipeWindow()
        
        # AdditionalRecipeWindow의 update_recipes 함수에 적절한 제목과 레시피 데이터 전달
        # 이제 clicked_food_name은 필요 없으므로 빈 문자열 또는 다른 적절한 값 전달
        self.additional_recipe_window.update_recipes("", additional_recommended_recipes)
        self.additional_recipe_window.show()


    def closeEvent(self, event):
        self.cap.release()
        cv2.destroyAllWindows()
        if self.recipe_window:
            self.recipe_window.close()
        if self.additional_recipe_window: # 추가 창도 닫기
            self.additional_recipe_window.close()
        super().closeEvent(event)