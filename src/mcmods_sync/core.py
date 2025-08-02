from . import config

from . import files as fileUtils
from . import server as serverUtils
from pathlib import Path


def setEnv(mods_path_: str|Path, prefix_: str, url_: str):
    config.setEnv(mods_path_, prefix_, url_)

def reDownloadAll(outputCli: bool = False):
    fileUtils.removeAll(outputCli)
    sync(outputCli)
    pass

def get_sync_plan(client: dict[str, str], server: dict[str, str]) -> tuple[list[str], list[str], list[str]]:
    to_add = []
    to_update = []
    to_delete = []

    for filename, server_hash in server.items():
        client_hash = client.get(filename)
        if client_hash is None:
            to_add.append(filename)
        elif client_hash != server_hash:
            to_update.append(filename)

    for filename in client:
        if filename not in server:
            to_delete.append(filename)

    return to_add, to_update, to_delete

def sync(outputCli: bool = False):
    # 取得伺服器那邊的檔案清單與SHA1
    server = serverUtils.Server()
    server.fetchMods()
    serverFileHashes = server.getModHashes()

    # 列出客戶端的檔案清單與SHA1
    clientFileHashes = fileUtils.getFileHashes()
    
    # 整理出需要處理的檔案清單
    addFilenames, updateFilenames, deleteFilenames = get_sync_plan(clientFileHashes, serverFileHashes)
    # print(addFilenames)

    # 下載新檔案、覆蓋新檔案
    for downloadFilename in addFilenames + updateFilenames:
        server.downloadModFile(downloadFilename, outputCli)
        
    # 刪除伺服器沒有的檔案
    for deleteFilename in deleteFilenames:
        fileUtils.remove(deleteFilename, outputCli)

def run(outputCli: bool = False):
    sync(outputCli)
    pass

if __name__ == "__main__":
    config.setEnv('/home/yuan/.local/share/PrismLauncher/instances/Barian/minecraft/mods/')
    # print(config.mods_path)
    run(True)
