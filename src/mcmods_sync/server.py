from . import config
from .files import getRawFilename
from urllib.parse import urljoin
from pathlib import Path
import requests
import io
import zipfile

class Server:
    # A class variable, counting the number of robots
    baseUrl = config.mcapiserver_url
    modsList = []

    def __init__(self):
        pass
    
    def fetchMods(self) -> requests.Response:
        url = urljoin(self.baseUrl, 'mods/?type=json')
        response = requests.get(url)

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

        return response

    def getModHashes(self) -> dict:
        hash_dict = { mod["filename"]: mod["sha1"] for mod in self.modsList }
        return hash_dict

    def getModFileDownloadUrls(self) -> dict:
        download_dict = { mod["filename"]: mod["downloadUrl"] for mod in self.modsList }
        return download_dict

    def downloadModFile(self, filename: str, outputCli: bool = False ):

        rawFilename = getRawFilename(filename)
        dest_path = Path(config.mods_path) / rawFilename
        url = self.getModFileDownloadUrls()[filename]
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                if outputCli:
                    print(f"下載: {response.status_code} "+url + " → " + str(dest_path))
                    
        else:
            print(f"下載失敗: {response.status_code} "+url)
    
    def downloadModFileZip(self, outputCli: bool = False ):
        extract_to = Path(config.mods_path)

        url = urljoin(self.baseUrl, 'zip/mods')
        prefix = config.prefix

        if outputCli:
            print(f"開始下載: "+url)
        response = requests.get(url)
        response.raise_for_status()
        if outputCli:
            print(f"下載完成: {response.status_code} "+url)

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            for member in zip_file.infolist():
                if member.is_dir():
                    continue  # 我們只處理檔案，資料夾會在建立時自動生成

                # 原始路徑分解
                original_path = Path(member.filename)
                parts = original_path.parts

                # 將每一層都加上 prefix（包含檔名）
                new_parts = [prefix + part for part in parts]
                new_path = extract_to.joinpath(*new_parts)

                # 確保目錄存在
                new_path.parent.mkdir(parents=True, exist_ok=True)

                # 寫入檔案
                with zip_file.open(member) as src, open(new_path, "wb") as dst:
                    dst.write(src.read())

                if outputCli:
                    print(f"解壓縮: " + str(new_path))


if __name__ == "__main__":
    server = Server()
    server.fetchMods()
    print(server.getModFileDownloadUrls())

    