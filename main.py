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


def parse_args():
    parser = argparse.ArgumentParser(description="Minecraft mods sync script")

    # PCL 模式使用
    parser.add_argument("--inst", help="Minecraft instance path (for PCL Launcher)")

    # 手動模式使用
    parser.add_argument("manual_path", nargs="?", help="Minecraft mods path (manual mode)")

    return parser.parse_args()

def detect_mc_dir():
    args = parse_args()

    # ✅ 新優先順序：手動 > --inst > 環境變數
    if args.manual_path:
        return Path(args.manual_path)
    elif args.inst:
        return Path(args.inst)
    elif "INST_MC_DIR" in os.environ:
        return Path(os.environ["INST_MC_DIR"])
    else:
        print("❌ 無法判斷 Minecraft mods 資料夾路徑！")
        print("請使用以下其中一種方式：")
        print("1. 手動執行：python main.py /your/minecraft/path")
        print("2. PCL Launcher：python main.py --inst /path")
        print("3. Prism Launcher：設定環境變數 INST_MC_DIR")
        sys.exit(1)

def main():
    mc_dir = detect_mc_dir()
    mods_dir = mc_dir / "mods"

    if not mods_dir.exists():
        print("⚠️ mods 資料夾不存在，將自動建立")
        mods_dir.mkdir(parents=True)

    # print(mods_dir)
    config.setEnv(mods_dir)
    core.run(True)

if __name__ == "__main__":
    main()
