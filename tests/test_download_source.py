import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mcmods_sync.download_source import select_download_url, DownloadSourceError


class TestDownloadSource(unittest.TestCase):
    def test_default_cdn(self):
        self.assertEqual(select_download_url({"downloadUrl": "https://cdn.example.org/mod.jar",
                                               "serverDownloadUrl": "https://mc.example.org/mod.jar"}),
                         "https://cdn.example.org/mod.jar")

    def test_prefer_origin(self):
        self.assertEqual(select_download_url({"downloadUrl": "https://cdn.example.org/mod.jar",
                                               "serverDownloadUrl": "https://mc.example.org/mod.jar"}, True),
                         "https://mc.example.org/mod.jar")

    def test_default_fallback_origin(self):
        self.assertEqual(select_download_url({"serverDownloadUrl": "https://mc.example.org/mod.jar"}),
                         "https://mc.example.org/mod.jar")

    def test_legacy(self):
        self.assertEqual(select_download_url({"downloadUrl": "https://old.example.org/mod.jar"}),
                         "https://old.example.org/mod.jar")

    def test_no_unsafe_fallback(self):
        with self.assertRaises(DownloadSourceError):
            select_download_url({"downloadUrl": "https://cdn.example.org/mod.jar"}, True)

    def test_nested_server_download(self):
        self.assertEqual(select_download_url({"links":{"serverDownloadUrl":"https://mc.example.org/a"}},True),
                         "https://mc.example.org/a")

    def test_invalid_scheme(self):
        with self.assertRaises(DownloadSourceError):
            select_download_url({"downloadUrl":"file:///etc/passwd"})

    def test_userinfo_rejected(self):
        with self.assertRaises(DownloadSourceError):
            select_download_url({"downloadUrl":"https://u:p@example.org/a"})


if __name__ == "__main__":
    unittest.main()
