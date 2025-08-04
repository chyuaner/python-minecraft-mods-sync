import sys
from PySide6.QtWidgets import QMainWindow
from .ui_mainwindow import Ui_MainWindow  # 生成的 UI 類
from PySide6.QtCore import QTimer, QCoreApplication

from mcmods_sync import config

class MainWindow(QMainWindow):
    isSkip = False
    def showInfo(self):
        self.ui.apiurl_label.setText(config.mcapiserver_url)
        self.ui.prefix_label.setText(config.prefix)
        self.ui.modsFolder_label.setText(str(config.mods_path))

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # 將 UI 佈局設到 self (QMainWindow)
        self.showInfo()

        # 你的事件連接與邏輯在這寫
        self.ui.skip_pBtn.clicked.connect(self.skipClick)
        self.ui.cancel_pBtn.clicked.connect(self.cancelClick)

    def skipClick(self):
        self.isSkip = True
        self.close()

    def cancelClick(self):
        self.close()

    def closeEvent(self, event):
        if self.isSkip:
            event.accept()
            self.exit_code = 0  # 設定你想傳出的退出碼

        else:
            event.accept()  # ✅ 先讓 Qt 結束事件流程
            self.exit_code = 1  # 設定你想傳出的退出碼

