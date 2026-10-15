from mcmods_sync import core
from PySide6.QtCore import QObject, Signal, QThread

class SyncWorker(QObject):
    progress = Signal(dict)
    finished = Signal(bool)  # True=成功, False=錯誤或取消
    error = Signal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        # 拿到目前的 thread 實體
        thread = QThread.currentThread()
        success = False

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
            self.error.emit("同步已取消")
        except Exception as exc:
            self.error.emit(f"同步失敗：{type(exc).__name__}: {exc}")
        else:
            if should_stop():
                self.error.emit("同步已取消")
            else:
                success = True
        finally:
            self.finished.emit(success)
