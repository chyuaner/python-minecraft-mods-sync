from mcmods_sync import  ProgressManager
from PySide6.QtCore import QObject, Signal

class SyncWorker(QObject):
    progress = Signal(dict)
    finished = Signal()

    def __init__(self):
        super().__init__()

    def run(self):
        # 傳入 self.progress.emit 作為 callback 來回報進度
        print("worker start")
        from mcmods_sync import core
        core.sync(outputCli=True, progress_callback=self.progress.emit)

        # core.sync(outputCli=True, progress_callback=None)
        self.finished.emit()
