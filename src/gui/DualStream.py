class DualStream:
    def __init__(self, qt_emitter, original_stream):
        self.qt_emitter = qt_emitter  # 是 EmittingStream 實例
        self.original_stream = original_stream  # sys.__stdout__ or sys.__stderr__

    def write(self, text):
        # if text.strip() == "":
        #     return
        # self.qt_emitter.text_written.emit(text)
        # self.original_stream.write(text)
        # self.original_stream.flush()

        try:
            if text.strip():
                # GUI內的CLI輸出
                self.qt_emitter.text_written.emit(text+"\n")
        except Exception:
            pass  # 不讓 Qt 錯誤影響 CLI

        try:
            # 傳統CLI輸出
            self.original_stream.write(text)
            self.original_stream.flush()
        except Exception:
            pass  # 防止 CLI 輸出錯誤阻斷程式

    def flush(self):
        self.original_stream.flush()
