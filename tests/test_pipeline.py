import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
from surveyor.core import JobStore
from surveyor.acquisition import Acquisition
from surveyor.pipeline import PipelineRequest,run_pipeline

class PipelineTests(unittest.TestCase):
    def test_rejects_unapproved_source(self):
        with self.assertRaises(ValueError):
            PipelineRequest("EMERSON","question","scope",("https://example.org/p",)).validate()
    def test_rejects_same_suite_reviewer(self):
        with self.assertRaises(ValueError):
            PipelineRequest("HADID","question","scope",reviewer_suite="HADID").validate()
    def test_offline_pipeline_with_source_and_peer(self):
        with TemporaryDirectory() as d:
            store=JobStore(Path(d)/"jobs.sqlite3")
            def acquire(url,archive,approved_hosts):
                payload=b"Morna is an established musical form in Cape Verde."
                digest=sha256(payload).hexdigest()
                (Path(archive)/(digest+".source")).write_bytes(payload)
                return Acquisition(url,digest,len(payload),"text/plain","2026-10-17T10:00:00Z")
            calls=[]
            def infer(suite,question,prompt):
                calls.append(suite)
                if suite=="EMERSON":
                    return {"model":"mock","response":json.dumps({"claims":[{"statement":"Morna is a musical form in Cape Verde"}]})}
                return {"response":json.dumps({"assessment":"supported","rationale":"Passage mentions the genre; further checking needed"})}
            request=PipelineRequest("EMERSON","Cape Verde music","Authorised preliminary research",
                                    ("https://example.org/a",),frozenset({"example.org"}),"CHAKOTAY")
            result=run_pipeline(store,request,Path(d),infer=infer,acquire=acquire)
            self.assertEqual(result["status"],"completed")
            self.assertEqual(calls,["EMERSON","CHAKOTAY"])
            self.assertEqual(result["claims"][0]["verification_status"],"unverified")
            self.assertEqual(result["claims"][0]["peer_review"]["status"],"model_proposal_only")
            self.assertTrue(result["claims"][0]["candidates"])
            self.assertEqual(store.get(result["job_id"])["status"],"completed")
            store.close()
    def test_no_sources_does_not_invent_sources(self):
        with TemporaryDirectory() as d:
            store=JobStore(Path(d)/"jobs.sqlite3")
            request=PipelineRequest("GOODALL","Biodiversity","")
            result=run_pipeline(store,request,d,infer=lambda *args:{"response":'{"claims":[{"statement":"A preliminary claim"}]}'})
            self.assertEqual(result["sources"],[])
            self.assertEqual(result["claims"][0]["candidates"],[])
            store.close()
    def test_bad_json_fails_and_records_error(self):
        with TemporaryDirectory() as d:
            store=JobStore(Path(d)/"jobs.sqlite3")
            with self.assertRaises(ValueError):
                run_pipeline(store,PipelineRequest("HADID","Buildings",""),d,
                             infer=lambda *args:{"response":"not json"})
            self.assertEqual(store.get(1)["status"],"failed")
            store.close()

if __name__=="__main__":
    unittest.main()
