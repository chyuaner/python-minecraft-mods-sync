from . import config
from pathlib import Path
import hashlib

def hashFolder():
    pass

def getFilePaths():
    mods_dir = Path(config.mods_path)
    jar_files = list(mods_dir.rglob(config.prefix+"*.jar"))
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
