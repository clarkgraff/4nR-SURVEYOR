"""D8C optional local faster-whisper speech recognition (no network fetching).

Operator must install the package and provide a pre-downloaded local model path.
"""
from pathlib import Path
from .media import get_media,verify_media
from .media_processing import extract_audio
from .language import transcript_record,save_transcript

def transcribe_local(archive,media_hash,*,model_path,device="cpu",compute_type="int8",
                     language=None):
    if not Path(model_path).is_dir():
        raise ValueError("A locally installed model directory is required")
    record=get_media(archive,media_hash)
    if not verify_media(record):
        raise ValueError("Source media integrity failure")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("Install optional faster-whisper dependency for transcription") from exc
    import av
    if int(av.__version__.split(".")[0]) >= 19:
        raise RuntimeError("faster-whisper 1.2.1 is incompatible with PyAV 19; install a compatible PyAV release (python -m pip install \"av>=17,<19\") before transcription")
    derivative=extract_audio(archive,media_hash)
    model=WhisperModel(str(model_path),device=device,compute_type=compute_type,
                       local_files_only=True)
    results,info=model.transcribe(derivative["path"],language=language,
                                  vad_filter=True,beam_size=5)
    segments=[{"start":float(item.start),"end":float(item.end),
               "text":item.text.strip()} for item in results if item.text.strip()]
    output=transcript_record(media_hash,info.language or language or "und",
                              segments,"faster-whisper",str(model_path))
    destination=save_transcript(output,archive)
    return {"schema":"surveyor.transcription-result.v0","transcript_path":str(destination),
            "media_sha256":media_hash,"language":output["language"],
            "segments":len(segments),"verification_status":output["verification_status"]}
