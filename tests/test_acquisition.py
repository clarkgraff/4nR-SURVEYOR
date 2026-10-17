import io
import tempfile
import unittest
from pathlib import Path
from surveyor.acquisition import fetch_source

class Headers(dict):
    def get_content_type(self):
        return self.get("Content-Type", "text/plain").split(";")[0]

class Response:
    status = 200
    def __init__(self, url, payload=b"relevant academic text", media_type="text/plain"):
        self.url, self.payload = url, payload
        self.headers = Headers({"Content-Type": media_type})
    def geturl(self):
        return self.url
    def read(self, n):
        return self.payload[:n]
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False

class Opener:
    def __init__(self, response):
        self.response = response
    def open(self, request, timeout=15):
        return self.response

class AcquisitionTests(unittest.TestCase):
    def test_retrieval_persists_bytes_and_not_reviewed_status(self):
        url = "https://example.org/article"
        with tempfile.TemporaryDirectory() as folder:
            event = fetch_source(url, folder, approved_hosts=frozenset({"example.org"}),
                                opener=Opener(Response(url)), dns_check=lambda host: None)
            self.assertEqual(event.review_status, "retrieved_not_reviewed")
            self.assertEqual((Path(folder) / (event.sha256_hex + ".source")).read_bytes(), b"relevant academic text")
            self.assertTrue((Path(folder) / "acquisitions.jsonl").exists())

    def test_host_requires_explicit_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                fetch_source("https://unapproved.example/item", folder,
                             approved_hosts=frozenset({"example.org"}), dns_check=lambda host: None)

    def test_local_ip_and_http_rejected(self):
        for url in ("http://example.org/a", "https://127.0.0.1/a", "https://example.org:8443/a"):
            with tempfile.TemporaryDirectory() as folder:
                with self.assertRaises(ValueError):
                    fetch_source(url, folder, approved_hosts=frozenset({"example.org"}),
                                 dns_check=lambda host: None)

    def test_overlimit_payload_rejected(self):
        url = "https://example.org/a"
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                fetch_source(url, folder, approved_hosts=frozenset({"example.org"}),
                             max_bytes=10, opener=Opener(Response(url, b"01234567890")),
                             dns_check=lambda host: None)

    def test_html_or_json_allowed_but_other_types_rejected(self):
        url = "https://example.org/a"
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                fetch_source(url, folder, approved_hosts=frozenset({"example.org"}),
                             opener=Opener(Response(url, media_type="application/pdf")),
                             dns_check=lambda host: None)

    def test_unexpected_redirect_target_rejected(self):
        url = "https://example.org/a"
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                fetch_source(url, folder, approved_hosts=frozenset({"example.org"}),
                             opener=Opener(Response("https://different.org/other")),
                             dns_check=lambda host: None)

if __name__ == "__main__":
    unittest.main()
