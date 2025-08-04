#!venv/bin/python3
import os
import sys
import argparse
from main import main as run_cli, parse_args as parse_args_cli, detect_mods_dir  # 匯入 CLI 模式邏輯
from PySide6.QtWidgets import QApplication

# 加入 src 目錄到 path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from gui.MainWindow import MainWindow

def parse_args():
    parser = argparse.ArgumentParser(description="Minecraft mods sync script")

    # 預計增加視窗化獨有參數
    # # 手動指定 mods 資料夾路徑
    # parser.add_argument("manual_path", nargs="?", help="Minecraft mods path (manual mode)")

    # # PrismCraft Launcher 使用的 instance 路徑
    # parser.add_argument("--inst", help="Minecraft instance path (for PCL Launcher)")

    return parse_args_cli(parser)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        run_cli()
    else:
        args = parse_args()
        mods_dir = detect_mods_dir(args)
        main()
    
