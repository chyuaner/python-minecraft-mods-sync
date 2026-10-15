"""Select a download source without silently ignoring explicit user preference.

This module intentionally has no Qt or network dependencies.
"""
from urllib.parse import urlsplit


class DownloadSourceError(ValueError):
    """The requested download source was missing or unsafe."""


def _get(mod: dict, name: str) -> str:
    links = mod.get("links") or {}
    value = mod.get(name) or (links.get(name) if isinstance(links, dict) else "")
    return value if isinstance(value, str) else ""


def _require_http_url(url: str, description: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in ("https", "http") or not parsed.netloc or parsed.username or parsed.password:
        raise DownloadSourceError(f"{description} 不存在或不是 HTTP(S) 網址")
    return url


def select_download_url(mod: dict, prefer_server: bool = False) -> str:
    """Choose a URL according to the MC8 plan.

    Default follows downloadUrl (CDN for public mods, origin for custom mods).
    --prefer-server MUST use serverDownloadUrl; never silently fall back
    to a CDN when direct-origin was explicitly requested.
    Legacy servers without serverDownloadUrl still work in default mode.
    """
    if prefer_server:
        return _require_http_url(_get(mod, "serverDownloadUrl"), "自建伺服器下載位址")

    url = _get(mod, "downloadUrl") or _get(mod, "download")
    if not url:
        url = _get(mod, "serverDownloadUrl")
    return _require_http_url(url, "下載位址")
