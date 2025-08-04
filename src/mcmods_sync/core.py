from . import config

from . import files as fileUtils
from . import server as serverUtils
from .ProgressManager import ProgressManager
from pathlib import Path


def setEnv(mods_path_: str|Path, prefix_: str, url_: str):
    config.setEnv(mods_path_, prefix_, url_)

def reDownloadAll(outputCli: bool = False, progress_callback=None):
    fileUtils.removeAll(outputCli)
    sync(outputCli)

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

def sync(outputCli: bool = False, progress_callback=None):
    steps = {
        "fetch_mods": 0.1,
        "download": 0.7,
        "delete": 0.2,
    }
    pm = ProgressManager(steps)
    
    # 取得伺服器那邊的檔案清單與SHA1
    server = serverUtils.Server()
    server.fetchMods()
    serverFileHashes = server.getModHashes()

    # 列出客戶端的檔案清單與SHA1
    clientFileHashes = fileUtils.getFileHashes()
    
    # 整理出需要處理的檔案清單
    addFilenames, updateFilenames, deleteFilenames = get_sync_plan(clientFileHashes, serverFileHashes)

    # 計算要處理的比例
    serverFileCount = len(serverFileHashes)
    processCount = len(addFilenames+updateFilenames)

    # 模擬 fetch_mods 100% 完成
    pm.update_step_progress(1.0)
    if progress_callback:
        progress_callback(pm.get_progress_info())

    # 下載步驟開始
    pm.start_step("download", file_count=processCount)

    # 若要處理的比例過高，嘗試走 zip 打包下載模式
    use_zip = (processCount / serverFileCount) > 0.7
    zip_failed = False

    if use_zip:
        try:
            server.downloadModFileZip(outputCli)

            # 整包下載視為完成整個下載步驟
            pm.update_step_progress(1.0)
            if progress_callback:
                progress_callback(pm.get_progress_info())

        except Exception as e:
            print(f"發生錯誤，將嘗試以單一檔案形式同步：{e}")
            zip_failed = True

    # 若 zip 模式沒用 or zip 模式失敗，就逐一下載
    if not use_zip or zip_failed:
        for i, downloadFilename in enumerate(addFilenames + updateFilenames):

            # 製作回報進度用callback
            def file_progress_cb(pct):
                # 更新檔案進度 (pct: 0~100)
                pm.update_file_progress(i, pct / 100)
                if progress_callback:
                    progress_callback(pm.get_progress_info())

            server.downloadModFile(downloadFilename, outputCli=outputCli, progress_callback=file_progress_cb)
        
    # 刪除伺服器沒有的檔案
    pm.start_step("delete", file_count=len(deleteFilenames))
    for i, deleteFilename in enumerate(deleteFilenames):
        fileUtils.remove(deleteFilename, outputCli)
        pm.update_file_progress(i, 1.0)
        if progress_callback:
            progress_callback(pm.get_progress_info())
        
def run(outputCli: bool = False):
    sync(outputCli)

