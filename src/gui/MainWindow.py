import sys
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QThread
from PySide6.QtGui import QTextCursor

from .ui_mainwindow import Ui_MainWindow
from .EmittingStream import EmittingStream
from .DualStream import DualStream
from .SyncWorker import SyncWorker

from mcmods_sync import config

class MainWindow(QMainWindow):
    isSkip = False
    totalProgress = 0

    def showInfo(self):
        self.ui.apiurl_label.setText(config.mcapiserver_url)
        self.ui.prefix_label.setText(config.prefix)
        self.ui.modsFolder_label.setText(str(config.mods_path))

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # 將 UI 佈局設到 self (QMainWindow)
        self.showInfo()

        # 建立 stream 並連接
        self.output_stream = EmittingStream()
        self.output_stream.text_written.connect(self.append_text)
        # sys.stdout = self.output_stream
        # sys.stderr = self.output_stream

        # 替換 stdout 和 stderr
        self.ui.output_textBrowser.setText("")
        sys.stdout = DualStream(self.output_stream, sys.__stdout__)
        sys.stderr = DualStream(self.output_stream, sys.__stderr__)

        # 你的事件連接與邏輯在這寫
        self.ui.skip_pBtn.clicked.connect(self.skipClick)
        self.ui.cancel_pBtn.clicked.connect(self.cancelClick)
        # 

    def append_text(self, text):
        self.ui.output_textBrowser.moveCursor(QTextCursor.End)
        self.ui.output_textBrowser.insertPlainText(text)

    def skipClick(self):
        self.isSkip = True
        self.close()

    def cancelClick(self):
        self.isSkip = False
        self.close()

    def closeEvent(self, event):
        if self.isSkip:
            event.accept()
            self.exit_code = 0  # 設定你想傳出的退出碼

        else:
            event.accept()  # ✅ 先讓 Qt 結束事件流程
            self.exit_code = 1  # 設定你想傳出的退出碼

    def start_sync(self):
        self.sync_thread = QThread()
        self.worker = SyncWorker()
        self.worker.moveToThread(self.sync_thread)

        self.sync_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.sync_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.sync_thread.finished.connect(self.sync_thread.deleteLater)

        # self.startBtn.setEnabled(False)
        # self.progressBar.setValue(0)
        self.on_start()
        self.sync_thread.start()

    def on_start(self):
        self.ui.total_progressBar.setValue(0)


    def on_progress(self, progress_info: dict):
        # 直接使用百分比，不要再乘以 100
        total_pct = progress_info.get("total_progress", 0)
        self.ui.total_progressBar.setValue(total_pct)

    def on_finished(self):
        # self.startBtn.setEnabled(True)
        # self.progressBar.setValue(100)
        print("同步完成")
        self.close()

