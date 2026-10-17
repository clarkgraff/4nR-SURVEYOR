import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from surveyor.vetting import (vet_claim, VettingPolicy, AuditLog, ImprovementProposal,
                             register_improvement)

CLAIM = {"statement": "An unverified music attribution"}
def candidate(identifier, url):
    return {"passage_id": identifier, "source_url": url,
            "verification_status": "candidate_only", "text": "Possible context"}

class VettingTests(unittest.TestCase):
    def test_supported_with_two_sources_still_unverified(self):
        result = vet_claim(CLAIM, [candidate("a","https://example.org/a"),
                                  candidate("b","https://example.net/b")],
                           assessor=lambda packet: {"assessment":"supported","rationale":"Two passages"})
        self.assertEqual(result["next_action"], "retain_for_review")
        self.assertEqual(result["verification_status"], "unverified")
        self.assertTrue(result["human_approval_required"])

    def test_model_agreement_with_one_source_does_not_certify(self):
        result=vet_claim(CLAIM,[candidate("a","https://example.org/a")],
                         assessor=lambda packet: {"assessment":"supported","rationale":"I agree"},
                         policy=VettingPolicy(max_investigations=0))
        self.assertEqual(result["next_action"],"investigate_further")

    def test_bounded_investigation_and_escalation(self):
        attempts=[]
        def investigate(packet, round_number):
            attempts.append(round_number)
            return []
        result=vet_claim(CLAIM,[],assessor=lambda packet:{"assessment":"insufficient","rationale":"No evidence"},
                         investigate=investigate,policy=VettingPolicy(max_investigations=2))
        self.assertEqual(attempts,[1,2])
        self.assertEqual(len(result["assessments"]),3)

    def test_contradiction_proposes_correction(self):
        result=vet_claim(CLAIM,[],assessor=lambda packet:{"assessment":"contradicted","rationale":"Conflicting source"})
        self.assertEqual(result["next_action"],"propose_correction")

    def test_dispute_escalates(self):
        result=vet_claim(CLAIM,[],assessor=lambda packet:{"assessment":"disputed","rationale":"Different accounts"})
        self.assertEqual(result["next_action"],"escalate_dispute")

    def test_malformed_assessor_rejected(self):
        with self.assertRaises(ValueError):
            vet_claim(CLAIM,[],assessor=lambda packet:{"assessment":"verified","rationale":"Claimed fact"})

    def test_log_roundtrip_and_detect_tampering(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/"audit.jsonl"
            log=AuditLog(path)
            log.append({"event_type":"vetting","outcome":"open"})
            log.append({"event_type":"vetting","outcome":"contested"})
            self.assertEqual(log.validate(),2)
            altered=path.read_text().replace("contested","cleared")
            path.write_text(altered)
            with self.assertRaises(ValueError):log.validate()

    def test_improvement_is_proposed_not_adopted(self):
        with TemporaryDirectory() as folder:
            log=AuditLog(Path(folder)/"audit.jsonl")
            proposal=ImprovementProposal("F-001","Model hallucination","Try a different retrieval strategy",
                                         "0/1 sourced claims","Held-out regional music facts")
            entry=register_improvement(log,proposal)
            self.assertFalse(entry["event"]["promotion_authorised"])
            self.assertEqual(log.validate(),1)

    def test_auto_promotion_disallowed(self):
        with self.assertRaises(ValueError):
            ImprovementProposal("F1","Issue","Change","Metric","Retest",status="adopted")
