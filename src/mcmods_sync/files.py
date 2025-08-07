from . import config
from pathlib import Path
import hashlib

def hashFolder():
    pass

# 搜尋檔名帶有prefix的檔名和資料夾
def getFilePaths():
    mods_dir = Path(config.mods_path)
    prefix = config.prefix
    jar_files = []
    
    for path in mods_dir.rglob(f"{prefix}*.jar"):
        # 取得 path 相對於 mods_dir 的路徑部分（只留下子路徑）
        try:
            relative_parts = path.relative_to(mods_dir).parts
        except ValueError:
            # 如果 path 不在 mods_dir 之下（理論上不會發生），跳過
            continue

        # 檢查所有中繼資料夾是否都以 barian_ 開頭（不檢查檔案本身）
        all_dirs_valid = all(
            part.startswith(prefix) for part in relative_parts[:-1]  # 最後一個是檔名
        )

        if all_dirs_valid:
            jar_files.append(path)

    return jar_files

def get_sha1(file_path: Path) -> str:
    hash_sha1 = hashlib.sha1()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

def getFileHashes() -> dict[str, str]:
    jar_files = getFilePaths()

    return {
        getFilenameFromRawFilename(jar.name): get_sha1(jar) for jar in jar_files
    }

def getFilenameFromRawFilename(raw_filename : str) -> str:
    return raw_filename.removeprefix(config.prefix)

def getRawFilename(filename : str) -> str:
    return config.prefix+getFilenameFromServerRawFilename(filename)

def getFilenameFromServerRawFilename(filename : str) -> str:
    suffix = '.client'
    return filename.removesuffix(suffix)

def remove(filename : str, outputCli: bool = False):
    dest_path = Path(config.mods_path) / getRawFilename(filename)

    if dest_path.exists():
        dest_path.unlink()  # 刪除檔案

    if outputCli:
        print(f"刪除: " + str(dest_path))

def removeAll(outputCli: bool = False):
    jar_files = getFilePaths()
    return {remove(getFilenameFromRawFilename(jar.name), outputCli) for jar in jar_files}
