from PySide6.QtWidgets import QMainWindow
from .ui_mainwindow import Ui_MainWindow  # 生成的 UI 類

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # 將 UI 佈局設到 self (QMainWindow)

        # 你的事件連接與邏輯在這寫
        self.ui.cancel_pBtn.clicked.connect(self.cancelClick)

    def cancelClick(self):
        print("按鈕被點了")
        self.close()

    def closeEvent(self, event):
        print("視窗關閉事件")
        event.accept()
        # event.ignore()