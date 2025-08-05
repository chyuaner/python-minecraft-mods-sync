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
    isFinal = False
    totalProgress = 0

    def showInfo(self):
        self.ui.apiurl_label.setText(config.mcapiserver_url)
        self.ui.prefix_label.setText(config.prefix)
        self.ui.modsFolder_label.setText(
            '<html><head/><body><p>'
            +'<a href="file://'+str(config.mods_path)+'"><span style=" text-decoration: underline; color:#2980b9;">'+str(config.mods_path)
            +'</span></a></p></body></html>'
            )

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # 將 UI 佈局設到 self (QMainWindow)
        self.showInfo()
        self.sync_thread = None

        # 隱藏目前暫無功能的Layout
        self.ui.extra_widget.setVisible(False)
        self.ui.step_widget.setVisible(False)

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
        self.ui.continue_pBtn.clicked.connect(self.skipClick)
        self.ui.exit_pBtn.clicked.connect(self.cancelClick)
        
        self.ui.finished_btnGroup.setVisible(False)

    def append_text(self, text):
        self.ui.output_textBrowser.moveCursor(QTextCursor.End)
        self.ui.output_textBrowser.insertPlainText(text)
        
    def skipClick(self):
        self.isSkip = True
        # self.isFinal = False
        self.close()

    def cancelClick(self):
        self.isSkip = False
        self.isFinal = False
        self.close()

    def closeEvent(self, event):
        self.exit_code = 0
        if self.sync_thread and self.sync_thread.isRunning():
            self.sync_thread.requestInterruption()
            # 等 thread 結束，阻塞 UI 不太好，可用非阻塞提示用戶
            self.sync_thread.finished.connect(lambda: self.close())  # 結束後再關閉
            event.ignore()  # 先不關閉視窗
            self.exit_code = 1

        else:
            if self.isSkip or self.isFinal:
                event.accept()
                self.exit_code = 0
            else:
                event.accept()
                self.exit_code = 1

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
        self.sync_thread.finished.connect(self.clear_sync_thread)
        
        # self.startBtn.setEnabled(False)
        # self.progressBar.setValue(0)
        self.on_start()
        self.sync_thread.start()

    def on_start(self):
        self.ui.total_progressBar.setValue(0)

    def on_progress(self, info: dict):
        self.ui.total_progressBar.setValue(int(info["total"] * 100))

        step_label_text = f"正在處理 {info['current_step']}"
        if info["file_count"] > 0:
            step_label_text += f" ({info['file_index']+1}/{info['file_count']})"
        if info.get('current_filename'):
            step_label_text += ": " + info['current_filename']
        self.ui.step_label.setText(step_label_text)
        # self.ui.step_progressBar.setValue(int(info["step_progress"] * 100))

        self.ui.file_progressBar.setValue(int(info["file_progress"] * 100))

    def on_finished(self, success: bool):
        print("同步完成" if success else "同步被中斷")
        self.isFinal = True if success else False

        self.ui.process_btnGroup.setVisible(False)
        self.ui.finished_btnGroup.setVisible(True)

    
    def clear_sync_thread(self):
        self.sync_thread = None
        if self.ui.finishNoClose_checkBox.isChecked() is not True:
            self.close()


