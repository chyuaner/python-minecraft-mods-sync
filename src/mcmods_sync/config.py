from pathlib import Path

mcapiserver_url = 'https://api-minecraft.yuaner.tw/'
prefix = 'barian_'
mods_path = 'mods'

def setEnv(mods_path_: str|Path, prefix_: str = prefix, url_: str = mcapiserver_url):
    global mcapiserver_url, prefix, mods_path
    mods_path = mods_path_
    prefix = prefix_
    mcapiserver_url = url_