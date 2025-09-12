#!venv/bin/python3
import os
import sys
import argparse
from pathlib import Path
from main import main as run_cli, parse_args as parse_args_cli, detect_mods_dir  # 匯入 CLI 模式邏輯
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog, QMessageBox

# 加入 src 目錄到 path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from gui.MainWindow import MainWindow
from mcmods_sync import core, config

def parse_args():
    parser = argparse.ArgumentParser(description="Minecraft mods sync script")

    # 預計增加視窗化獨有參數
    # # 手動指定 mods 資料夾路徑
    # parser.add_argument("manual_path", nargs="?", help="Minecraft mods path (manual mode)")

    # # PrismCraft Launcher 使用的 instance 路徑
    # parser.add_argument("--inst", help="Minecraft instance path (for PCL Launcher)")

    return parse_args_cli(parser)

def main():
    # print(mods_dir)
    global mods_dir
    dMcapiserver_url, dPrefix, dMods_path = config.getDefault()

    app = QApplication(sys.argv)
    if mods_dir is None:
        window = QMainWindow()
        folderPath = QFileDialog.getExistingDirectory(window, "選擇 Minecraft mods 資料夾")
        if folderPath:
            mods_dir = Path(folderPath)
            config.setModFolderMethod = '手動指定'
        else:
            # ❌ 使用者未選擇資料夾，程式中止
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Critical)
            msgBox.setWindowTitle("無法繼續執行")
            msgBox.setText(
                "無法判斷 Minecraft mods 資料夾路徑！\n"
                "請先選擇 Mods 資料夾\n\n"
                "或是使用以下其中一種方式：\n"
                "1. 手動執行：python main.py /your/minecraft/mods\n"
                "2. PCL Launcher：python main.py --inst /your/instance/path\n"
                "3. Prism Launcher：請設定環境變數 INST_MC_DIR\n"
                "或將執行檔放置在 Minecraft 實例資料夾底下"
            )
            msgBox.exec()
            sys.exit(1)

    core.setEnv(mods_dir, args.prefix, args.remote)

    win = MainWindow()
    win.show()
    win.start_sync()
    app.exec()
    sys.exit(win.exit_code)

if __name__ == '__main__':
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        run_cli()
    else:
        args = parse_args()
        mods_dir = detect_mods_dir(args)
        main()
    
