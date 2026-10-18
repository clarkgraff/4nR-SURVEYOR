import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from surveyor.language import transcript_record,save_transcript,subtitles
from surveyor.transcript_review import corrected_transcript

class TranscriptReviewTests(unittest.TestCase):
    def test_revision_preserves_original_and_timecodes(self):
        with TemporaryDirectory() as root:
            original=save_transcript(transcript_record("a"*64,"en",
                [{"start":1.0,"end":3.0,"text":"Lidafor"}],"whisper","small"),root)
            before=original.read_bytes()
            revision=corrected_transcript(original,{0:"Lita Ford"},
                operator="Operator",reason="Name confirmed by listener",archive=root)
            result=json.loads(revision.read_text(encoding="utf-8"))
            self.assertEqual(original.read_bytes(),before)
            self.assertEqual(result["segments"][0]["text"],"Lita Ford")
            self.assertEqual(result["segments"][0]["start"],1.0)
            self.assertEqual(result["verification_status"],"human_corrected_not_fact_verified")
            self.assertIn("Lita Ford",subtitles(result))
            self.assertEqual(result["corrections"][0]["previous"],"Lidafor")

    def test_requires_operator_reason_and_valid_index(self):
        with TemporaryDirectory() as root:
            original=save_transcript(transcript_record("a"*64,"en",
                [{"start":0,"end":1,"text":"hello"}],"whisper","small"),root)
            for kwargs in ({"operator":"","reason":"reason"},
                           {"operator":"Operator","reason":""}):
                with self.assertRaises(ValueError):
                    corrected_transcript(original,{0:"goodbye"},archive=root,**kwargs)
            with self.assertRaises(ValueError):
                corrected_transcript(original,{2:"goodbye"},operator="Operator",
                                     reason="review",archive=root)

    def test_revision_chain_keeps_prior_original(self):
        with TemporaryDirectory() as root:
            original=save_transcript(transcript_record("a"*64,"en",
                [{"start":0,"end":1,"text":"one"}],"whisper","small"),root)
            revision=corrected_transcript(original,{0:"two"},operator="Operator",
                                          reason="review",archive=root)
            second=corrected_transcript(revision,{0:"three"},operator="Operator",
                                         reason="second review",archive=root)
            doc=json.loads(second.read_text(encoding="utf-8"))
            self.assertEqual(doc["segments"][0]["text"],"three")
            self.assertEqual(json.loads(original.read_text())["segments"][0]["text"],"one")
            self.assertTrue(revision.exists())

if __name__=="__main__": unittest.main()
