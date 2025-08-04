from PySide6.QtCore import QObject, Signal

class EmittingStream(QObject):
    text_written = Signal(str)

    def write(self, text):
        self.text_written.emit(str(text))

    def flush(self):
        pass  # 可選，如果你用 print(..., flush=True) 可能需要這個
