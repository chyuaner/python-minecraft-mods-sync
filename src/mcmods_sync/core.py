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

def sync(outputCli: bool = False, progress_callback=None, should_stop=None):
    # 原始權重設定（可視需求調整）
    base_weights = {
        "fetch_mods": 0.1,
        "download": 0.7,
        "delete": 0.2,
    }
    pm = ProgressManager(base_weights)
    # fetch_mods 步驟開始
    pm.start_step("fetch_mods")

    # 取得完後標示完成
    pm.update_step_progress(0)
    if progress_callback:
        progress_callback(pm.get_progress_info())
    
    # 取得伺服器那邊的檔案清單與SHA1
    server = serverUtils.Server()
    server.fetchMods()
    if should_stop and should_stop():
        raise KeyboardInterrupt("中止同步作業")
    serverFileHashes = server.getModHashes()

    # 列出客戶端的檔案清單與SHA1
    clientFileHashes = fileUtils.getFileHashes()
    if should_stop and should_stop():
        raise KeyboardInterrupt("中止同步作業")
    
    # 整理出需要處理的檔案清單
    addFilenames, updateFilenames, deleteFilenames = get_sync_plan(clientFileHashes, serverFileHashes)

    # 實際有需要執行的步驟 (fetch_mods一定執行)
    active_steps = {
        "fetch_mods": base_weights["fetch_mods"],
        "download": base_weights["download"] if (len(addFilenames) + len(updateFilenames)) > 0 else 0.0,
        "delete": base_weights["delete"] if len(deleteFilenames) > 0 else 0.0,
    }

    # 正規化權重，確保加起來是1
    total_weight = sum(active_steps.values()) or 1
    steps = {k: v / total_weight for k, v in active_steps.items()}

    pm = ProgressManager(steps)

    # fetch_mods 步驟開始
    pm.start_step("fetch_mods")

    # 取得完後標示完成
    pm.update_step_progress(1.0)
    if progress_callback:
        progress_callback(pm.get_progress_info())

    # 計算要處理的比例
    serverFileCount = len(serverFileHashes)
    processCount = len(addFilenames+updateFilenames)

    # 模擬 fetch_mods 100% 完成
    pm.update_step_progress(1.0)
    if progress_callback:
        progress_callback(pm.get_progress_info())
    if should_stop and should_stop():
        raise KeyboardInterrupt("中止同步作業")

    # 下載步驟開始
    # 若要處理的比例過高，嘗試走 zip 打包下載模式
    use_zip = (processCount / serverFileCount) > 0.7
    zip_failed = False

    if use_zip:
        try:
            pm.start_step("download", file_count=1)

            # 製作回報進度用callback
            def file_progress_cb(pct):
                # 更新檔案進度 (pct: 0~100)
                pm.update_file_progress(0, pct / 100)
                if progress_callback:
                    progress_callback(pm.get_progress_info())
            if should_stop and should_stop():
                raise KeyboardInterrupt("中止同步作業")
            server.downloadModFileZip(outputCli, progress_callback=file_progress_cb, should_stop=should_stop)

        except Exception as e:
            print(f"發生錯誤，將嘗試以單一檔案形式同步：{e}")
            zip_failed = True

    # 若 zip 模式沒用 or zip 模式失敗，就逐一下載
    if not use_zip or zip_failed:
        pm.start_step("download", file_count=processCount)
        for i, downloadFilename in enumerate(addFilenames + updateFilenames):
            if should_stop and should_stop():
                raise KeyboardInterrupt("中止同步作業")
            # 製作回報進度用callback
            def file_progress_cb(pct):
                # 更新檔案進度 (pct: 0~100)
                pm.update_file_progress(i, pct / 100)
                if progress_callback:
                    progress_callback(pm.get_progress_info())
            server.downloadModFile(downloadFilename, outputCli=outputCli, progress_callback=file_progress_cb, should_stop=should_stop)
        
    # 刪除伺服器沒有的檔案
    pm.start_step("delete", file_count=len(deleteFilenames))
    if len(deleteFilenames) == 0:
        # 沒有刪除檔案，直接把 delete 步驟進度設為 100%
        pm.update_step_progress(1.0)
        if progress_callback:
            progress_callback(pm.get_progress_info())
    else:
        for i, deleteFilename in enumerate(deleteFilenames):
            if should_stop and should_stop():
                raise KeyboardInterrupt("中止同步作業")
            fileUtils.remove(deleteFilename, outputCli)
            pm.update_file_progress(i, 1.0)
            if progress_callback:
                progress_callback(pm.get_progress_info())
    
        
def run(outputCli: bool = False):
    sync(outputCli)

