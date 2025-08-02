from . import config
from .files import getRawFilename
from urllib.parse import urljoin
from pathlib import Path
import requests

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

if __name__ == "__main__":
    server = Server()
    server.fetchMods()
    print(server.getModFileDownloadUrls())

    