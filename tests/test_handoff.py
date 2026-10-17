import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from contextlib import redirect_stdout
from surveyor.core import JobStore
from surveyor.presentation import present, save_presentation, record_decision
from surveyor.handoff import create_handoff, execute_handoff
from surveyor.vetting import AuditLog
from surveyor.__main__ import main

def make_source(root):
    source=Path(root)/"discovery.json"
    source.write_text(json.dumps({
       "schema":"surveyor.discovery.v0","suite":"EMERSON","query":"Morna",
       "results":[{"title":"UNESCO morna","provider":"youtube",
                   "url":"https://www.youtube.com/watch?v=example"}]}),encoding="utf-8")
    return save_presentation(present(source),root)

class HandoffTests(unittest.TestCase):
    def test_requires_recorded_explicit_decision(self):
        with TemporaryDirectory() as root:
            store=JobStore(Path(root)/"jobs.db")
            presentation=make_source(root)
            with self.assertRaises(ValueError):
                create_handoff(store,presentation,1,"Investigate",archive=root)
            store.close()

    def test_queued_handoff_preserves_no_content_approval(self):
        with TemporaryDirectory() as root:
            store=JobStore(Path(root)/"jobs.db")
            presentation=make_source(root)
            record_decision(presentation,1,"investigate_further","Operator","Check UNESCO",archive=root)
            output=create_handoff(store,presentation,1,"Check UNESCO",archive=root)
            self.assertEqual(output["status"],"queued")
            self.assertFalse(output["acquisition_approved"])
            self.assertEqual(output["source_content_status"],"not_acquired")
            self.assertEqual(store.get(output["job_id"])["status"],"queued")
            self.assertEqual(AuditLog(Path(root)/"investigation-handoffs.jsonl").validate(),1)
            store.close()

    def test_handoff_completes_with_unverified_presentation(self):
        with TemporaryDirectory() as root:
            store=JobStore(Path(root)/"jobs.db")
            presentation=make_source(root)
            record_decision(presentation,1,"investigate_further","Operator","Check UNESCO",archive=root)
            job=create_handoff(store,presentation,1,"Check UNESCO",archive=root)["job_id"]
            def infer(*args):
                return {"response":'{"claims":[{"statement":"Morna is a musical tradition"}]}'}
            result=execute_handoff(store,job,archive=root,infer=infer)
            self.assertEqual(result["status"],"completed")
            self.assertEqual(store.get(job)["status"],"completed")
            expanded=json.loads(Path(result["presentation_path"]).read_text(encoding="utf-8"))
            self.assertEqual(len(expanded["claims"]),1)
            self.assertEqual(expanded["research_verification"],"not_verified")
            store.close()

    def test_cli_decision_automatically_queues_job(self):
        with TemporaryDirectory() as root:
            presentation=make_source(root)
            out=io.StringIO()
            argv=["surveyor","--db",str(Path(root)/"jobs.db"),"decide",str(presentation),
                  "1","investigate_further","--operator","Operator",
                  "--reason","Research morna", "--archive",root]
            with patch("sys.argv",argv),redirect_stdout(out):
                main()
            result=json.loads(out.getvalue())
            self.assertEqual(result["handoff"]["status"],"queued")

if __name__=="__main__":
    unittest.main()
