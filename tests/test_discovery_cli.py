"""Exercise the D6A PowerShell-facing CLI without live network access."""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from surveyor.__main__ import main

class DiscoveryCLITests(unittest.TestCase):
    def test_discovery_command_archives_report(self):
        with TemporaryDirectory() as folder:
            manifest=Path(folder)/"manifest.json"
            manifest.write_text(json.dumps([{
                "provider":"youtube","url":"https://youtube.com/watch?v=test",
                "title":"Morna music in Cape Verde", "kind":"video"}]))
            output=io.StringIO()
            argv=["surveyor","--db",str(Path(folder)/"jobs.db"),"discover",
                  "EMERSON","Morna Cape Verde","--provider","youtube",
                  "--manifest",str(manifest),"--archive",folder]
            with patch.object(sys,"argv",argv),redirect_stdout(output):
                main()
            report=json.loads(output.getvalue())
            self.assertEqual(report["results"][0]["evidence_status"],"discovery_only")
            self.assertTrue(Path(report["archive_path"]).is_file())

if __name__=="__main__":
    unittest.main()
