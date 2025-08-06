from . import config
from .files import getRawFilename, getFilenameFromServerRawFilename
from urllib.parse import urljoin
from pathlib import Path
import requests
import io
import zipfile
from urllib.parse import unquote, unquote_to_bytes
import re

class Server:
    # A class variable, counting the number of robots
    baseUrl = config.mcapiserver_url
    modsList = []

    def __init__(self):
        pass

    def fetchMods(self, outputCli: bool = False) -> requests.Response:
        url = urljoin(self.baseUrl, 'mods/?type=json')
        response = requests.get(url)
        if outputCli:
            print(f"連接伺服器: {response.status_code} "+url)

        if response.status_code == 200:
            # 預期拿到
            data = response.json()  # 直接取得 JSON 內容 (dict)

            if isinstance(data, dict) and isinstance(data.get("mods"), list):
                for mod in data["mods"]:
                    mod_info = {
                        "name": mod.get("name", ""),
                        "version": mod.get("version", ""),
                        "filename": mod.get("filename", ""),
                        "sha1": mod.get("sha1", ""),
                        "downloadUrl": mod.get("downloadUrl") or mod.get("download") or "",
                    }
                    self.modsList.append(mod_info)
        
        # GUI顯示Extra資訊
        config.modsCount = len(self.modsList)

        return response

    def getModHashes(self) -> dict:
        hash_dict = { getFilenameFromServerRawFilename(mod["filename"]): mod["sha1"] for mod in self.modsList }
        return hash_dict

    def getModFileDownloadUrls(self) -> dict:
        download_dict = { getFilenameFromServerRawFilename(mod["filename"]): mod["downloadUrl"] for mod in self.modsList }
        return download_dict

    def downloadModFile(self, filename: str, outputCli: bool = False, progress_callback = None, should_stop=None):

        rawFilename = getRawFilename(filename)
        dest_path = Path(config.mods_path) / rawFilename
        url = self.getModFileDownloadUrls()[filename]
        response = requests.get(url, stream=True)
        total_length_str = response.headers.get('Content-Length')
        if outputCli:
            print(f"下載: {response.status_code} "+url + " → " + str(dest_path))

        if response.status_code == 200:
            downloaded_length = 0
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if should_stop and should_stop():
                        raise KeyboardInterrupt("中止同步作業")
                    if chunk:
                        f.write(chunk)
                        downloaded_length += len(chunk)

                        if progress_callback:
                            if total_length_str is not None:
                                total_length = int(total_length_str)
                                progress = int(downloaded_length / total_length * 100)
                                progress_callback(progress)
                            else:
                                progress = int(0)
                                progress_callback(progress)
                    
        else:
            print(f"下載失敗: {response.status_code} "+url)
    
    def downloadModFileZip(self, outputCli: bool = False, progress_callback=None, should_stop=None, filename_holder: list[str] = None):
        def extract_filename_from_disposition(disposition: str) -> str:
            # RFC 5987: filename*=UTF-8''...
            match = re.search(r"filename\*\s*=\s*(?:UTF-8'')?([^;\r\n]+)", disposition, re.IGNORECASE)
            if match:
                try:
                    return unquote_to_bytes(match.group(1)).decode("utf-8")
                except Exception as e:
                    print(f"[解析錯誤] filename* 無法解碼：{e}")

            # fallback: filename="..."
            match = re.search(r'filename="?([^";\r\n]+)"?', disposition)
            if match:
                return match.group(1)  # 通常是 ASCII，直接回傳即可

            return "all_mods.zip"

        extract_to = Path(config.mods_path)
        url = urljoin(self.baseUrl, 'zip/mods')
        prefix = config.prefix

        if outputCli:
            print(f"開始下載: " + url)

        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_length_str = response.headers.get('Content-Length')
        total_length = int(total_length_str) if total_length_str and total_length_str.isdigit() else None

        disposition = response.headers.get('Content-Disposition', '')
        filename = extract_filename_from_disposition(disposition)

        if filename_holder is not None and isinstance(filename_holder, list) and len(filename_holder) > 0:
            filename_holder[0] = filename

        buffer = io.BytesIO()
        downloaded_length = 0

        for chunk in response.iter_content(chunk_size=8192):
            if should_stop and should_stop():
                raise KeyboardInterrupt("中止同步作業")
            if chunk:
                buffer.write(chunk)
                downloaded_length += len(chunk)

                if progress_callback and total_length:
                    progress = downloaded_length / total_length
                    # progress_callback 期待0~1或0~100？
                    progress_callback({
                        "stage": "download",
                        "progress": int(progress * 100),
                    })

        if outputCli:
            print(f"下載完成: {response.status_code} " + url)

        buffer.seek(0)  # 重設指標到開頭

        # --- ZIP 解壓縮階段 ---
        with zipfile.ZipFile(buffer) as zip_file:
            members = [m for m in zip_file.infolist() if not m.is_dir()]
            total_files = len(members)
            extracted_count = 0

            if progress_callback:
                progress_callback({
                    "stage": "start_extract",
                    "file_count": total_files
                })

            for member in members:
                if should_stop and should_stop():
                    raise KeyboardInterrupt("中止同步作業")

                original_path = Path(member.filename)
                new_parts = [getRawFilename(part) for part in original_path.parts]
                new_path = extract_to.joinpath(*new_parts)
                new_path.parent.mkdir(parents=True, exist_ok=True)

                with zip_file.open(member) as src, open(new_path, "wb") as dst:
                    dst.write(src.read())

                extracted_count += 1

                if outputCli:
                    print(f"解壓縮: {new_path}")

                if progress_callback:
                    progress_callback({
                        "stage": "extract",
                        "progress": extracted_count / total_files,
                        "current_file": str(member.filename),
                        "done_files": extracted_count,
                        "total_files": total_files,
                    })

            # ✅ 解壓縮完成，標記 extract_zip 步驟為 100%
            if progress_callback:
                progress_callback({
                    "stage": "extract_complete"
                })
    