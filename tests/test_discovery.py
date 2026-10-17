import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from surveyor.discovery import SOURCES, DiscoveryRequest, DiscoveryHit, rank_hits, discover, save_report
from surveyor.discovery_connectors import manifest_connector

class DiscoveryTests(unittest.TestCase):
    def test_all_children_have_sources(self):
        self.assertEqual(len(SOURCES),6)
        self.assertIn("bandcamp",SOURCES["EMERSON"])
        self.assertIn("architecture_publication",SOURCES["HADID"])

    def test_rejects_cross_discipline_provider(self):
        with self.assertRaises(ValueError):
            DiscoveryRequest("HADID","architecture",("bandcamp",)).validate()

    def test_requires_installed_connector(self):
        with self.assertRaisesRegex(ValueError, "not installed"):
            discover(DiscoveryRequest("EMERSON","music",("youtube",)),{})

    def test_filters_results_and_ranks_matches(self):
        req=DiscoveryRequest("EMERSON","Cape Verde morna",("youtube",),max_results=2)
        hits=[
            DiscoveryHit("youtube","https://example.com/c","Other topic"),
            DiscoveryHit("youtube","https://example.com/a","Cape Verde morna",kind="video"),
            DiscoveryHit("youtube","https://example.com/a#timestamp","Duplicate Cape Verde"),
        ]
        result=rank_hits(req,hits)
        self.assertEqual(len(result),2)
        self.assertEqual(result[0]["url"],"https://example.com/a")
        self.assertFalse(result[0]["approved_for_acquisition"])

    def test_rejects_invalid_scheme(self):
        with self.assertRaises(ValueError):
            DiscoveryHit("youtube","http://example.org/a","Unsafe").validate()

    def test_prevents_unrequested_provider_mixing(self):
        with self.assertRaises(ValueError):
            rank_hits(DiscoveryRequest("GOODALL","ocean",("university",)),
                      [DiscoveryHit("instagram","https://example.org/p","ocean")])

    def test_offline_manifest_roundtrip(self):
        with TemporaryDirectory() as folder:
            file=Path(folder)/"sources.json"
            file.write_text(json.dumps([
                {"provider":"bandcamp","url":"https://example.org/artist",
                 "title":"Cape Verde musicians","kind":"person"},
                {"provider":"youtube","url":"https://example.org/video",
                 "title":"Cape Verde music","kind":"video"}
            ]),encoding="utf-8")
            request=DiscoveryRequest("EMERSON","Cape Verde",("bandcamp",))
            report=discover(request,{"bandcamp":manifest_connector(file,"bandcamp")})
            self.assertEqual(len(report["results"]),1)
            self.assertEqual(report["verification_status"],"not_verified")
            saved=save_report(report,folder)
            self.assertEqual(json.loads(saved.read_text())["schema"],"surveyor.discovery.v0")

    def test_rejects_manifest_unknown_fields(self):
        with TemporaryDirectory() as folder:
            file=Path(folder)/"sources.json"
            file.write_text('[{"provider":"youtube","url":"https://example.org","title":"x","verified":true}]')
            with self.assertRaises(ValueError):
                manifest_connector(file,"youtube")("test",5)
