import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from surveyor.media import import_media, get_media, verify_media
from surveyor.media_processing import probe_media, extract_audio

class MediaTests(unittest.TestCase):
    def test_local_import_and_provenance(self):
        with TemporaryDirectory() as root:
            file=Path(root)/"voice.wav"
            file.write_bytes(b"RIFF"+b"x"*100)
            record=import_media(file,root,operator="Operator",
                                licence_basis="Owned recording")
            self.assertEqual(record["schema"],"surveyor.media.v0")
            self.assertEqual(record["sha256_hex"],hashlib.sha256(file.read_bytes()).hexdigest())
            self.assertEqual(record["verification_status"],"not_verified")
            self.assertTrue(verify_media(record))
            self.assertEqual(get_media(root,record["sha256_hex"]),record)

    def test_deduplicate_and_tamper_detection(self):
        with TemporaryDirectory() as root:
            file=Path(root)/"voice.wav"
            file.write_bytes(b"RIFF"+b"12345")
            one=import_media(file,root,operator="Operator",licence_basis="Owned")
            two=import_media(file,root,operator="Operator",licence_basis="Owned")
            self.assertEqual(one["content_path"],two["content_path"])
            Path(one["content_path"]).write_bytes(b"altered")
            self.assertFalse(verify_media(one))
            with self.assertRaises(ValueError):
                import_media(file,root,operator="Operator",licence_basis="Owned")

    def test_permission_and_file_rejection(self):
        with TemporaryDirectory() as root:
            file=Path(root)/"voice.wav"
            file.write_bytes(b"123")
            with self.assertRaises(ValueError):
                import_media(file,root,operator="",licence_basis="Owned")
            with self.assertRaises(ValueError):
                import_media(file,root,operator="Operator",licence_basis="")
            bad=Path(root)/"executable.exe"
            bad.write_bytes(b"123")
            with self.assertRaises(ValueError):
                import_media(bad,root,operator="Operator",licence_basis="Owned")

    def test_probe_uses_existing_content(self):
        with TemporaryDirectory() as root:
            file=Path(root)/"voice.wav"
            file.write_bytes(b"RIFF123")
            record=import_media(file,root,operator="Operator",licence_basis="Owned")
            class Result:
                stdout='{"streams":[{"codec_type":"audio"}],"format":{"duration":"5"}}'
            with patch("surveyor.media_processing.subprocess.run",return_value=Result()) as run:
                out=probe_media(root,record["sha256_hex"])
            self.assertEqual(out["streams"][0]["codec_type"],"audio")
            self.assertEqual(out["verification_status"],"technical_metadata_only")
            self.assertEqual(run.call_args.kwargs["timeout"],120)

    def test_audio_extraction_produces_derived_record(self):
        with TemporaryDirectory() as root:
            file=Path(root)/"voice.wav"
            file.write_bytes(b"RIFF123")
            record=import_media(file,root,operator="Operator",licence_basis="Owned")
            def fake_run(args,**kwargs):
                Path(args[-1]).write_bytes(b"RIFF-derived")
            with patch("surveyor.media_processing.subprocess.run",side_effect=fake_run):
                out=extract_audio(root,record["sha256_hex"])
            self.assertEqual(out["parent_sha256"],record["sha256_hex"])
            self.assertEqual(Path(out["path"]).read_bytes(),b"RIFF-derived")

if __name__=="__main__": unittest.main()
