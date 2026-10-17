import tempfile
import unittest
from pathlib import Path
from surveyor.core import JobStore, Mission, Surveyor, SUITES


class SurveyorFoundationTests(unittest.TestCase):
    def test_all_six_suites_registered(self):
        self.assertEqual(set(SUITES), {"CHEKOV", "EMERSON", "BOURDAIN", "CHAKOTAY", "GOODALL", "HADID"})

    def test_invalid_suite_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            store = JobStore(Path(folder) / "test.sqlite")
            with self.assertRaises(ValueError):
                store.submit(Mission("UNKNOWN", "Hello"))
            store.close()

    def test_persistence_dispatch_and_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "test.sqlite"
            store = JobStore(database)
            job = store.submit(Mission("EMERSON", "Describe local instruments"))
            result = Surveyor(store, executor=lambda suite, question: {"suite": suite, "response": question, "source_status": "test"}).dispatch(job)
            self.assertEqual(result["suite"], "EMERSON")
            store.close()
            reopened = JobStore(database)
            self.assertEqual(reopened.get(job)["status"], "completed")
            reopened.close()

    def test_cancel_and_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            store = JobStore(Path(folder) / "test.sqlite")
            job = store.submit(Mission("GOODALL", "Survey"))
            store.cancel(job)
            self.assertEqual(store.get(job)["status"], "cancelled")
            store.resume(job)
            self.assertEqual(store.get(job)["status"], "queued")
            store.close()

    def test_failed_executor_recorded(self):
        with tempfile.TemporaryDirectory() as folder:
            store = JobStore(Path(folder) / "test.sqlite")
            job = store.submit(Mission("HADID", "Describe construction"))
            def fail(suite, question):
                raise RuntimeError("runtime unavailable")
            with self.assertRaises(RuntimeError):
                Surveyor(store, executor=fail).dispatch(job)
            self.assertEqual(store.get(job)["status"], "failed")
            store.close()

if __name__ == "__main__":
    unittest.main()
