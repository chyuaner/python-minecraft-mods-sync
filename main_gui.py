#!venv/bin/python3
import os
import sys
from PySide6.QtWidgets import QApplication

# 加入 src 目錄到 path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from gui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
