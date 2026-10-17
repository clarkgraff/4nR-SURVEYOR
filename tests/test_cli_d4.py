"""CLI command contract tests; mock the inference layer, never access network."""
import io
import json
import unittest
from contextlib import redirect_stdout, redirect_stderr
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
from surveyor.__main__ import main

class D4CLITests(unittest.TestCase):
    def invoke(self, arguments):
        stream = io.StringIO()
        with patch("sys.argv", ["surveyor", *arguments]), redirect_stdout(stream):
            main()
        return stream.getvalue()

    def test_cli_pipeline_dispatch_and_persistence(self):
        with TemporaryDirectory() as folder:
            db = str(Path(folder) / "research.sqlite3")
            archive = str(Path(folder) / "archive")
            model_output = {"model":"mock","response":json.dumps({"claims":[{"statement":"Provisional statement"}]})}
            with patch("surveyor.pipeline.lemonade_chat", return_value=model_output):
                out = self.invoke(["--db",db,"pipeline","EMERSON","Test question",
                                   "--scope","Pilot","--archive",archive])
            report = json.loads(out)
            self.assertEqual(report["status"],"completed")
            self.assertEqual(report["claims"][0]["verification_status"],"unverified")
            self.assertEqual(report["sources"],[])
            self.assertIn('"status": "completed"',self.invoke(["--db",db,"get",str(report["job_id"])]))

    def test_download_without_explicit_consent_rejected(self):
        with TemporaryDirectory() as folder:
            args=["--db",str(Path(folder)/"job.sqlite3"),
                  "pipeline","GOODALL","Test","--source","https://example.org/a",
                  "--approve-host","example.org"]
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as e:
                self.invoke(args)
            self.assertEqual(e.exception.code,2)

    def test_consented_download_without_source_rejected(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as e:
            self.invoke(["pipeline","GOODALL","Test","--allow-download"])
        self.assertEqual(e.exception.code,2)

    def test_invalid_reviewer_rejected(self):
        with tempfile_dir() as folder:
            with self.assertRaises(ValueError):
                self.invoke(["--db",str(Path(folder)/"job.sqlite3"),"pipeline",
                             "HADID","Test","--reviewer","HADID"])

def tempfile_dir():
    return TemporaryDirectory()

if __name__ == "__main__":
    unittest.main()
