import tempfile
import unittest
from pathlib import Path
from surveyor.core import JobStore
from surveyor.specialists import SPECIALISTS, system_prompt
from surveyor.orchestrator import ResearchRequest, run_research

class SpecialistTests(unittest.TestCase):
    def test_profiles_have_six_distinct_identities(self):
        self.assertEqual(len(SPECIALISTS), 6)
        for name in SPECIALISTS:
            self.assertIn("SURVEYOR-" + name, system_prompt(name))
    def test_navigational_authority(self):
        prompt = system_prompt("CHEKOV", "Cape Verde")
        self.assertIn("NERDS must independently verify", prompt)
        self.assertIn("Cape Verde", prompt)
    def test_invalid_and_duplicate_specialists_rejected(self):
        for suites in [(), ("EMERSON", "EMERSON"), ("OTHER",)]:
            with self.assertRaises(ValueError):
                ResearchRequest("Research subject", suites).validate()
    def test_two_children_record_independent_durable_jobs(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "research.sqlite"
            store = JobStore(db)
            observed = []
            def infer(suite, question, prompt):
                observed.append((suite, prompt))
                return {"response": "TEST ONLY"}
            report = run_research(store, ResearchRequest("Atlantic culture", ("EMERSON", "CHAKOTAY")), infer)
            self.assertEqual(report["status"], "completed")
            self.assertEqual(len(observed), 2)
            self.assertNotEqual(report["job_ids"][0], report["job_ids"][1])
            store.close()
            reopened = JobStore(db)
            for job_id in report["job_ids"]:
                self.assertEqual(reopened.get(job_id)["status"], "completed")
            reopened.close()
    def test_fail_closed_after_error(self):
        with tempfile.TemporaryDirectory() as folder:
            store = JobStore(Path(folder) / "research.sqlite")
            def fail(suite, question, prompt):
                raise RuntimeError("simulated outage")
            report = run_research(store, ResearchRequest("subject", ("EMERSON", "HADID")), fail)
            self.assertEqual(report["status"], "partial_failure")
            self.assertEqual(len(report["job_ids"]), 1)
            self.assertEqual(store.get(report["job_ids"][0])["status"], "failed")
            store.close()

if __name__ == "__main__":
    unittest.main()
