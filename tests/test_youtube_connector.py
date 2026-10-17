"""D6B provider contract tests; no live API requests."""
import io
import json
import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory
from pathlib import Path
from surveyor.youtube_connector import youtube_connector, parse_youtube_search
from surveyor.discovery import DiscoveryRequest, discover, save_report

DATA={"items":[
 {"id":{"kind":"youtube#video","videoId":"abc123"},
  "snippet":{"title":"Morna in Cape Verde","description":"Traditional music","channelTitle":"Musician A","publishedAt":"2025-01-01T00:00:00Z"}},
 {"id":{"kind":"youtube#channel","channelId":"UCabc"},
  "snippet":{"title":"Artist channel","channelTitle":"Artist channel"}},
 {"id":{"kind":"youtube#playlist","playlistId":"PLabc"},"snippet":{"title":"Ignored playlist"}}
]}

class MockResponse:
    headers={"Content-Type":"application/json; charset=UTF-8"}
    def __init__(self,body):
        self.body=io.BytesIO(body)
    def read(self,n=-1):return self.body.read(n)
    def __enter__(self):return self
    def __exit__(self,*args):pass

class YouTubeConnectorTests(unittest.TestCase):
    def test_video_and_channel_parsing(self):
        hits=parse_youtube_search(DATA)
        self.assertEqual(len(hits),2)
        self.assertEqual(hits[0].kind,"video")
        self.assertIn("watch?v=abc123",hits[0].url)
        self.assertEqual(hits[1].kind,"channel")
    def test_requires_api_key(self):
        with patch.dict("os.environ",{"SURVEYOR_YOUTUBE_API_KEY":""}):
            with self.assertRaises(ValueError):
                youtube_connector()
    def test_api_request_and_no_key_in_results(self):
        requested=[]
        def opener(request,timeout):
            requested.append(request.full_url)
            return MockResponse(json.dumps(DATA).encode("utf-8"))
        connector=youtube_connector(api_key="TEST-KEY-DO-NOT-SEND",opener=opener)
        hits=connector("Cape Verde",5)
        self.assertIn("TEST-KEY-DO-NOT-SEND",requested[0])
        self.assertEqual(len(hits),2)
        self.assertNotIn("TEST-KEY-DO-NOT-SEND",str(hits))
        report=discover(DiscoveryRequest("EMERSON","Morna",("youtube",)),{"youtube":connector})
        self.assertEqual(report["verification_status"],"not_verified")
        with TemporaryDirectory() as folder:
            path=save_report(report,folder)
            self.assertNotIn("TEST-KEY-DO-NOT-SEND",path.read_text())
    def test_rejects_bad_api_response(self):
        with self.assertRaises(ValueError):parse_youtube_search({"items":{}})
    def test_rejects_html_response(self):
        class HTML(MockResponse):
            headers={"Content-Type":"text/html"}
        connector=youtube_connector(api_key="fake",opener=lambda request,timeout:HTML(b"<html></html>"))
        with self.assertRaises(ValueError):connector("music",3)
    def test_rejects_oversize_response(self):
        connector=youtube_connector(api_key="fake",opener=lambda request,timeout:MockResponse(b"x"*(1024*1024+1)))
        with self.assertRaises(ValueError):connector("music",3)
    def test_rejects_excessive_limit(self):
        connector=youtube_connector(api_key="fake",opener=lambda request,timeout:MockResponse(b"{}"))
        with self.assertRaises(ValueError):connector("music",51)
if __name__=="__main__":unittest.main()
