"""D5 integrated review semantics: no model certification."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from surveyor.core import JobStore
from surveyor.pipeline import PipelineRequest, run_pipeline
from surveyor.vetting import AuditLog

class D5IntegrationTests(unittest.TestCase):
    def test_requires_independent_reviewer(self):
        with self.assertRaises(ValueError):
            PipelineRequest("EMERSON","Music","",vetting_enabled=True).validate()

    def test_missing_sources_remains_unverified_and_audited(self):
        with TemporaryDirectory() as root:
            store=JobStore(Path(root)/"jobs.sqlite3")
            def infer(suite,question,prompt):
                if suite=="EMERSON":
                    return {"response":json.dumps({"claims":[{"statement":"Unconfirmed musical style"}]})}
                return {"response":json.dumps({"assessment":"supported","rationale":"An unsupported model opinion"})}
            result=run_pipeline(store,PipelineRequest("EMERSON","Music","",reviewer_suite="CHAKOTAY",
                                                       vetting_enabled=True),root,infer=infer)
            entry=result["claims"][0]
            self.assertEqual(entry["verification_status"],"unverified")
            self.assertEqual(entry["vetting"]["next_action"],"investigate_further")
            self.assertEqual(entry["vetting"]["assessments"][0]["distinct_source_candidates"],0)
            self.assertEqual(AuditLog(Path(root)/"vetting-audit.jsonl").validate(),1)
            self.assertEqual(store.get(result["job_id"])["status"],"completed")
            store.close()

    def test_contradiction_flags_correction_without_certification(self):
        with TemporaryDirectory() as root:
            store=JobStore(Path(root)/"jobs.sqlite3")
            def infer(suite,question,prompt):
                if suite=="EMERSON":
                    return {"response":'{"claims":[{"statement":"Invented genre"}]}'}
                return {"response":'{"assessment":"contradicted","rationale":"Reference conflict reported"}'}
            result=run_pipeline(store,PipelineRequest("EMERSON","Find genre","",reviewer_suite="CHAKOTAY",
                                                       vetting_enabled=True),root,infer=infer)
            self.assertEqual(result["claims"][0]["vetting"]["next_action"],"propose_correction")
            self.assertTrue(result["claims"][0]["vetting"]["human_approval_required"])
            store.close()

    def test_bad_vetting_json_fails_job(self):
        with TemporaryDirectory() as root:
            store=JobStore(Path(root)/"jobs.sqlite3")
            def infer(suite,question,prompt):
                return {"response":'{"claims":[{"statement":"Test claim"}]}' if suite=="EMERSON" else "nonsense"}
            with self.assertRaises(ValueError):
                run_pipeline(store,PipelineRequest("EMERSON","Test","",reviewer_suite="CHAKOTAY",
                                                   vetting_enabled=True),root,infer=infer)
            self.assertEqual(store.get(1)["status"],"failed")
            store.close()

if __name__=="__main__":
    unittest.main()
