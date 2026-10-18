import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from surveyor.language import (transcript_record,save_transcript,subtitles,
                              translation_record,validate_segments)
from surveyor.transcription import transcribe_local

HASH="a"*64
SEGMENTS=[{"start":0.0,"end":1.5,"text":"Hello world"},
          {"start":2.0,"end":3.125,"text":"Morna is beautiful"}]

class LanguageTests(unittest.TestCase):
    def test_transcript_archive_and_provenance(self):
        with TemporaryDirectory() as root:
            record=transcript_record(HASH,"en",SEGMENTS,"test","model")
            path=save_transcript(record,root)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")),record)
            self.assertEqual(path,save_transcript(record,root))
            self.assertEqual(record["verification_status"],"machine_generated_unreviewed")

    def test_srt_timecodes(self):
        record=transcript_record(HASH,"en",SEGMENTS,"test","model")
        result=subtitles(record)
        self.assertIn("00:00:00,000 --> 00:00:01,500",result)
        self.assertIn("00:00:02,000 --> 00:00:03,125",result)
        self.assertIn("Morna is beautiful",result)

    def test_vtt_timecodes(self):
        record=transcript_record(HASH,"en",SEGMENTS,"test","model")
        result=subtitles(record,"vtt")
        self.assertTrue(result.startswith("WEBVTT"))
        self.assertIn("00:00:02.000 --> 00:00:03.125",result)

    def test_timecode_validation(self):
        for bad in ([{"start":1,"end":1,"text":"a"}],
                    [{"start":2,"end":3,"text":"a"},{"start":1,"end":4,"text":"b"}],
                    [{"start":-1,"end":0,"text":"a"}],
                    [{"start":0,"end":1,"text":12}]):
            with self.assertRaises(ValueError):
                validate_segments(bad)

    def test_translation_is_separate_unverified_record(self):
        record=translation_record("transcript-hash","fr",SEGMENTS,"human-draft")
        self.assertEqual(record["schema"],"surveyor.translation.v0")
        self.assertEqual(record["verification_status"],"machine_generated_unreviewed")

    def test_local_model_required_without_loading_dependencies(self):
        with TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                transcribe_local(root,HASH,model_path=Path(root)/"missing")

if __name__=="__main__":unittest.main()
