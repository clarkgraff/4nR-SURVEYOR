import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from contextlib import redirect_stdout
from surveyor.presentation import present,save_presentation,record_decision
from surveyor.vetting import AuditLog
from surveyor.__main__ import main

def fixture(root):
    file=Path(root)/"discovery.json"
    file.write_text(json.dumps({"schema":"surveyor.discovery.v0","suite":"EMERSON",
      "query":"Cape Verde morna","results":[
        {"title":"UNESCO Morna","provider":"youtube",
         "url":"https://www.youtube.com/watch?v=example","creator":"UNESCO"}]}))
    return file

class PresentationTests(unittest.TestCase):
    def test_present_link_metadata_not_evidence(self):
        with TemporaryDirectory() as root:
            result=present(fixture(root))
            self.assertEqual(result["sources"][0]["status"],"discovery_only")
            self.assertEqual(result["research_verification"],"not_verified")
            self.assertEqual(result["claims"],[])

    def test_reject_cross_suite_investigation(self):
        with TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                present(fixture(root),pipeline_result={"schema":"surveyor.pipeline.v0","suite":"HADID","claims":[]})

    def test_claim_draft_never_verified_by_presentation(self):
        with TemporaryDirectory() as root:
            result=present(fixture(root),pipeline_result={"schema":"surveyor.pipeline.v0",
                 "suite":"EMERSON","job_id":4,"claims":[{"draft":{"statement":"Unconfirmed genre"},
                   "verification_status":"verified"}]})
            self.assertEqual(result["claims"][0]["verification_status"],"unverified")

    def test_user_decisions_append_and_remain_not_verified(self):
        with TemporaryDirectory() as root:
            path=save_presentation(present(fixture(root)),root)
            result=record_decision(path,1,"approve","Clark","Review for filming",archive=root)
            self.assertFalse(result["approved_as_evidence"])
            self.assertEqual(result["verification_status"],"not_verified")
            self.assertEqual(AuditLog(Path(root)/"presentation-decisions.jsonl").validate(),1)

    def test_invalid_item_and_empty_reason_rejected(self):
        with TemporaryDirectory() as root:
            path=save_presentation(present(fixture(root)),root)
            with self.assertRaises(ValueError):
                record_decision(path,2,"approve","Operator","Reason",archive=root)
            with self.assertRaises(ValueError):
                record_decision(path,1,"flag_correct","Operator","",archive=root)

    def test_powershell_cli_present_and_decide(self):
        with TemporaryDirectory() as root:
            source=fixture(root)
            out=io.StringIO()
            with patch("sys.argv",["surveyor","--db",str(Path(root)/"jobs.db"),"present",str(source),
                                    "--archive",root]),redirect_stdout(out):
                main()
            report=json.loads(out.getvalue())
            self.assertTrue(Path(report["presentation_path"]).exists())
            out=io.StringIO()
            with patch("sys.argv",["surveyor","--db",str(Path(root)/"jobs.db"),"decide",
                                    report["presentation_path"],"1","save_for_later",
                                    "--operator","Clark","--reason","Revisit","--archive",root]),redirect_stdout(out):
                main()
            self.assertEqual(json.loads(out.getvalue())["action"],"save_for_later")
