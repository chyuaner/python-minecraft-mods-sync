#!/usr/bin/env python3

import os
import sys
import argparse
from pathlib import Path

# 加入 src 目錄到 path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from mcmods_sync import core, config

# Prism Launcher
# 預啟動指令會在實例啟動前執行，而結束後指令則會在其結束後執行。
# 此兩者會在啟動器的工作目錄中執行並附加額外的環境變數：
# $INST_NAME──實例的名稱
# $INST_ID──實例的 ID（其資料夾名稱）
# $INST_DIR──實例的絕對路徑
# $INST_MC_DIR──Minecraft 的絕對路徑
# $INST_JAVA──啟動所用的 Java 執行檔
# $INST_JAVA_ARGS──啟動所用的命令列引數
# 包裝指令允許啟動時使用額外的包裝程式（如 Linux 中的「optirun」）
#     INST_NAME: "Barian",
#     INST_ID: "Barian",
#     INST_DIR──實例的絕對路徑: "/home/yuan/.local/share/PrismLauncher/instances/Barian",
#     INST_MC_DIR: "/home/yuan/.local/share/PrismLauncher/instances/Barian/minecraft",
#     INST_JAVA: "/home/yuan/.local/share/PrismLauncher/java/java-runtime-delta/bin/java",
#     INST_JAVA_ARGS: "-Xms512m -Xmx4096m -Duser.language=en"

# PCL Launcher
# 在 MC 启动前执行特定命令或程序，语法与 Windows 的命令提示符一致。

# 可以使用以下替换标记实现相对路径（路径均以 \ 结尾）：
#  · {path}：PCL 的 exe 文件所在的文件夹
#  · {minecraft}：.minecraft 文件夹
#  · {verpath}：实例文件夹（.minecraft\versions\实例名\）
#  · {verindie}：开启版本隔离时等同实例文件夹，未开启时等同 .minecraft 文件夹
#  · {java}：游戏运行时的 Java 文件夹

# 除此之外，也支持以下替换标记：
#  · {user}：玩家名字
#  · {login}：玩家的登录方式
#  · {uuid}：玩家的 UUID
#  · {name}：游戏实例名
#  · {date}、{time}：当前的系统时间
#  · {version}：游戏对应的原版版本号

# 例如：
#  · "{verpath}test.exe" ：运行实例文件夹下的 test.exe 程序
#  · "{java}java.exe" -jar "{verpath}test.jar" ：用 Java 运行实例文件夹下的 test.jar
#  · notepad "{verindie}options.txt" ：使用记事本打开该实例的设置文件

# 涉及路径的操作最好都打上双引号，以避免路径中的空格导致运行失败。
# 执行命令时，命令行所在的目录是当前的 .minecraft 文件夹。


def parse_args(parser = argparse.ArgumentParser(description="Minecraft mods sync script")):
    
    # 手動指定 mods 資料夾路徑
    parser.add_argument("manual_path", nargs="?", help="Minecraft mods path (manual mode)")

    # PrismCraft Launcher 使用的 instance 路徑
    parser.add_argument("--inst", help="Minecraft instance path (for PCL Launcher)")

    return parser.parse_args()

def is_minecraft_instance_dir(path: Path) -> bool:
    # 必須有 mods 資料夾
    if not (path / "mods").is_dir():
        return False
    # 判斷其他常見 Minecraft 實例特徵
    has_config = (path / "config").is_dir()
    has_logs = (path / "logs").is_dir()
    has_options = (path / "options.txt").is_file()
    count = sum([has_config, has_logs, has_options])
    # 有兩個以上條件成立就認定是 Minecraft 實例資料夾
    return count >= 2

def detect_mods_dir(args=None) -> Path|None:
    if args is None:
        args = parse_args()

    # 1. 手動參數
    if args.manual_path:
        return Path(args.manual_path)

    # 2. --inst 參數
    if args.inst:
        return Path(args.inst) / "mods"

    # 3. 環境變數
    if "INST_MC_DIR" in os.environ:
        return Path(os.environ["INST_MC_DIR"]) / "mods"

    # 4. 判斷執行檔目錄是否為 Minecraft 實例資料夾
    if getattr(sys, 'frozen', False):
        exec_path = Path(sys.executable).resolve().parent
    else:
        exec_path = Path(__file__).resolve().parent

    if is_minecraft_instance_dir(exec_path):
        return exec_path / "mods"

    # 5. 無法判斷
    return None

def main():
    args = parse_args()
    mods_dir = detect_mods_dir(args)

    if mods_dir is None:
        # 5. 失敗提示
        print("❌ 無法判斷 Minecraft mods 資料夾路徑！")
        print("請使用以下其中一種方式：")
        print("1. 手動執行：python main.py /your/minecraft/mods")
        print("2. PCL Launcher：python main.py --inst /your/instance/path")
        print("3. Prism Launcher：請設定環境變數 INST_MC_DIR")
        print("或將執行檔放置在 Minecraft 實例資料夾底下")
        sys.exit(1)

    if not mods_dir.exists():
        print("⚠️ mods 資料夾不存在，將自動建立")
        mods_dir.mkdir(parents=True)

    # print(mods_dir)
    config.setEnv(mods_dir)
    core.run(True)

if __name__ == "__main__":
    main()
