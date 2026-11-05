import json
import tempfile
import unittest
from pathlib import Path

from surveyor.chakotay import build_dossier, save_dossier


def sample_pipeline():
    return {
        "schema": "surveyor.pipeline.v0",
        "suite": "CHAKOTAY",
        "status": "completed",
        "job_id": 42,
        "question": "Historical and cultural research",
        "claims": [{
            "draft": {
                "suite": "CHAKOTAY",
                "statement": "Illustrative research claim requiring verification",
                "temporal_context": "Illustrative historical period",
                "geographic_context": "Test destination",
                "uncertainty": "Unverified",
            },
            "candidates": [{
                "passage_id": "test:0",
                "source_url": "https://example.org/source",
                "text": "Illustrative passage",
                "verification_status": "candidate_only",
            }],
        }],
    }


class ChakotayTests(unittest.TestCase):

    def test_dossier_preserves_claim_and_provenance(self):
        dossier = build_dossier(
            "Test destination",
            sample_pipeline(),
            themes={1: "history"},
        )
        self.assertEqual(dossier["suite"], "CHAKOTAY")
        self.assertEqual(dossier["claims"][0]["theme"], "history")
        self.assertEqual(
            dossier["claims"][0]["candidate_passages"][0]["passage_id"],
            "test:0",
        )
        self.assertEqual(dossier["verification_status"], "unverified")

    def test_chronology_is_not_claimed_verified(self):
        dossier = build_dossier("Test", sample_pipeline())
        self.assertEqual(len(dossier["chronology"]), 1)
        self.assertEqual(
            dossier["chronology"][0]["verification_status"],
            "unverified",
        )

    def test_rejects_other_specialist(self):
        pipeline = sample_pipeline()
        pipeline["suite"] = "CHEKOV"
        with self.assertRaises(ValueError):
            build_dossier("Test", pipeline)

    def test_rejects_invalid_theme(self):
        with self.assertRaises(ValueError):
            build_dossier(
                "Test",
                sample_pipeline(),
                themes={1: "verified_history"},
            )

    def test_contributor_discovery_remains_unapproved(self):
        discovery = {
            "schema": "surveyor.discovery.v0",
            "suite": "CHAKOTAY",
            "results": [{
                "kind": "person",
                "title": "Illustrative researcher",
                "url": "https://example.org/researcher",
                "provider": "university",
            }],
        }
        dossier = build_dossier(
            "Test",
            sample_pipeline(),
            discovery_report=discovery,
        )
        self.assertEqual(len(dossier["contributors"]), 1)
        self.assertEqual(
            dossier["contributors"][0]["editorial_status"],
            "pending_review",
        )
        self.assertEqual(
            dossier["contributors"][0]["contact_status"],
            "not_contacted",
        )

    def test_immutable_dossier_save(self):
        dossier = build_dossier("Test", sample_pipeline())
        with tempfile.TemporaryDirectory() as folder:
            first = save_dossier(dossier, folder)
            second = save_dossier(dossier, folder)
            self.assertEqual(first, second)
            self.assertEqual(
                json.loads(first.read_text(encoding="utf-8"))["suite"],
                "CHAKOTAY",
            )
            self.assertEqual(
                len(list(Path(folder).rglob("*.json"))),
                1,
            )


if __name__ == "__main__":
    unittest.main()