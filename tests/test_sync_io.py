import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mcmods_sync import config
from mcmods_sync.server import Server
from mcmods_sync.download_source import DownloadSourceError


class FakeResponse:
    status_code = 200
    def __init__(self, payload: bytes):
        self.payload = payload
        self.headers = {"Content-Length": str(len(payload))}

    def iter_content(self, chunk_size=8192):
        yield self.payload

    def raise_for_status(self):
        pass


class TestSingleDownload(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = (config.mods_path, config.prefix, config.prefer_server)
        config.mods_path = Path(self.tmp.name)
        config.prefix = "barian_"
        config.prefer_server = False
        self.payload = b"a good mod jar"
        self.filename = "example.jar"
        self.expected = hashlib.sha1(self.payload).hexdigest()
        self.server = Server()
        self.server.modsList = [{"filename": self.filename,
                                 "sha1": self.expected,
                                 "downloadUrl": "https://cdn.example.com/example.jar",
                                 "serverDownloadUrl": "https://mc.example.com/example.jar"}]

    def tearDown(self):
        config.mods_path, config.prefix, config.prefer_server = self.old
        self.tmp.cleanup()

    @patch("mcmods_sync.server.requests.get")
    def test_default_download_and_checksum(self, get):
        get.return_value = FakeResponse(self.payload)
        self.server.downloadModFile(self.filename)
        self.assertEqual((Path(self.tmp.name) / "barian_example.jar").read_bytes(), self.payload)
        self.assertEqual(get.call_args.args[0], "https://cdn.example.com/example.jar")

    @patch("mcmods_sync.server.requests.get")
    def test_irrelevant_missing_origin_does_not_block_download(self, get):
        self.server.modsList.append({"filename": "other.jar",
                                     "sha1": self.expected,
                                     "downloadUrl": "https://cdn.example.com/other.jar",
                                     "serverDownloadUrl": ""})
        get.return_value = FakeResponse(self.payload)
        config.prefer_server = True
        self.server.downloadModFile(self.filename)
        self.assertEqual(get.call_args.args[0], "https://mc.example.com/example.jar")

    @patch("mcmods_sync.server.requests.get")
    def test_prefer_server_download(self, get):
        get.return_value = FakeResponse(self.payload)
        config.prefer_server = True
        self.server.downloadModFile(self.filename)
        self.assertEqual(get.call_args.args[0], "https://mc.example.com/example.jar")

    @patch("mcmods_sync.server.requests.get")
    def test_corrupted_content_keeps_old_file(self, get):
        get.return_value = FakeResponse(b"bad data")
        dest = Path(self.tmp.name) / "barian_example.jar"
        dest.write_bytes(b"old bytes")
        with self.assertRaisesRegex(ValueError, "SHA1"):
            self.server.downloadModFile(self.filename)
        self.assertEqual(dest.read_bytes(), b"old bytes")
        self.assertFalse((Path(self.tmp.name) / "barian_example.jar.mcmods_sync.part").exists())

    @patch("mcmods_sync.server.requests.get")
    def test_interruption_keeps_old_file(self, get):
        get.return_value = FakeResponse(self.payload)
        dest = Path(self.tmp.name) / "barian_example.jar"
        dest.write_bytes(b"old bytes")
        with self.assertRaises(KeyboardInterrupt):
            self.server.downloadModFile(self.filename, should_stop=lambda: True)
        self.assertEqual(dest.read_bytes(), b"old bytes")

    @patch("mcmods_sync.server.requests.get")
    def test_error_propagates(self, get):
        get.side_effect = OSError("network down")
        with self.assertRaises(OSError):
            self.server.downloadModFile(self.filename)

    @patch("mcmods_sync.server.requests.get")
    def test_explicit_origin_missing_does_not_fallback(self, get):
        config.prefer_server = True
        self.server.modsList[0]["serverDownloadUrl"] = ""
        with self.assertRaises(DownloadSourceError):
            self.server.downloadModFile(self.filename)
        get.assert_not_called()

    def test_fresh_instances(self):
        self.assertEqual(Server().modsList, [])

if __name__ == "__main__":
    unittest.main()
