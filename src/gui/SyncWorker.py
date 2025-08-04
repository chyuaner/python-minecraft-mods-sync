from mcmods_sync import core
from PySide6.QtCore import QObject, Signal, QThread

class SyncWorker(QObject):
    progress = Signal(dict)
    finished = Signal()

    def __init__(self):
        super().__init__()

    def run(self):
        # 拿到目前的 thread 實體
        thread = QThread.currentThread()

        # 傳入中斷檢查函式
        def should_stop():
            return thread.isInterruptionRequested()

        try:
            core.sync(
                outputCli=True,
                progress_callback=self.progress.emit,
                should_stop=should_stop
            )
        except KeyboardInterrupt:
            print("Sync 被中止")
        finally:
            self.finished.emit()
