import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from food_detection import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(model_path="best.pt")
    window.show()
    sys.exit(app.exec())