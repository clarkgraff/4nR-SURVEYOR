import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from hashlib import sha256
from surveyor.research_index import source_text,passages_from_text,candidate_passages,index_acquisition
from surveyor.claim_review import parse_claim_drafts,cross_agent_review_packet,record_human_review
from surveyor.acquisition import Acquisition

class D2Tests(unittest.TestCase):
    def test_html_excludes_scripts(self):
        result=source_text(b"<p>Cape Verde</p><script>badscript</script><p>Morna</p>","text/html")
        self.assertIn("Morna",result);self.assertNotIn("badscript",result)
    def test_passage_index_roundtrip(self):
        with TemporaryDirectory() as d:
            data=b"Cape Verde morna music";digest=sha256(data).hexdigest()
            (Path(d)/(digest+".source")).write_bytes(data)
            a=Acquisition("https://example.org/a",digest,len(data),"text/plain","2026-10-17T00:00:00Z")
            self.assertEqual(len(index_acquisition(d,a)),1)
            self.assertTrue((Path(d)/(digest+".passages.json")).exists())
    def test_archive_tampering_rejected(self):
        with TemporaryDirectory() as d:
            digest=sha256(b"original").hexdigest()
            (Path(d)/(digest+".source")).write_bytes(b"altered")
            a=Acquisition("https://example.org/a",digest,8,"text/plain","2026-10-17T00:00:00Z")
            with self.assertRaises(ValueError):index_acquisition(d,a)
    def test_candidate_is_not_corroboration(self):
        p=passages_from_text("Morna traditions in Cape Verde","abc","https://example.org")
        self.assertEqual(candidate_passages("Cape Verde morna",p)[0]["verification_status"],"candidate_only")
    def test_structured_claim_extraction(self):
        c=parse_claim_drafts(json.dumps({"claims":[{"statement":"Morna is a music genre"}]}),"EMERSON")
        self.assertEqual(c[0].suite,"EMERSON")
    def test_model_cannot_assert_verification(self):
        with self.assertRaises(ValueError):
            parse_claim_drafts('{"claims":[{"statement":"Fact","verified":true}]}',"EMERSON")
    def test_unstructured_response_rejected(self):
        with self.assertRaises(json.JSONDecodeError):parse_claim_drafts("Plain narrative","HADID")
    def test_review_packet_has_no_verdict(self):
        claim=parse_claim_drafts('{"claims":[{"statement":"Historical subject"}]}',"CHAKOTAY")[0]
        self.assertEqual(cross_agent_review_packet(claim,"EMERSON",[])["review_status"],"awaiting_review")
    def test_same_suite_cannot_review(self):
        claim=parse_claim_drafts('{"claims":[{"statement":"A claim"}]}',"GOODALL")[0]
        with self.assertRaises(ValueError):cross_agent_review_packet(claim,"GOODALL",[])
    def test_human_review_append_only(self):
        claim=parse_claim_drafts('{"claims":[{"statement":"A claim"}]}',"BOURDAIN")[0]
        with TemporaryDirectory() as d:
            path=Path(d)/"review.jsonl"
            record_human_review(path,claim,"Reviewer","insufficient","Missing evidence",[])
            record_human_review(path,claim,"Reviewer","supported","New source",["passage-1"])
            self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()),2)
