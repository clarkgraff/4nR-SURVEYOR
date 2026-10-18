"""D8C language records: immutable machine output, separate revisions and subtitles."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

def _timestamp(seconds: float, *, vtt: bool=False) -> str:
    if seconds < 0: raise ValueError("Negative timecode")
    milliseconds=round(seconds*1000)
    hours,remainder=divmod(milliseconds,3600000)
    minutes,remainder=divmod(remainder,60000)
    secs,ms=divmod(remainder,1000)
    return f"{hours:02}:{minutes:02}:{secs:02}{'.' if vtt else ','}{ms:03}"

def validate_segments(segments):
    if not isinstance(segments,list): raise ValueError("Segments must be a list")
    previous=0
    for segment in segments:
        if not isinstance(segment,dict) or not isinstance(segment.get("text"),str):
            raise ValueError("Malformed transcript segment")
        a,b=segment.get("start"),segment.get("end")
        if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or not (0<=a<b):
            raise ValueError("Invalid timecode range")
        if a<previous: raise ValueError("Transcript must be ordered")
        previous=b

def transcript_record(media_hash,language,segments,engine,model):
    if len(media_hash)!=64 or not language or not engine or not model:
        raise ValueError("Missing transcript provenance")
    validate_segments(segments)
    return {"schema":"surveyor.transcript.v0","media_sha256":media_hash,
            "language":language,"engine":engine,"model":model,
            "segments":segments,"verification_status":"machine_generated_unreviewed",
            "created_utc":datetime.now(timezone.utc).isoformat()}

def save_transcript(record,archive):
    if record.get("schema")!="surveyor.transcript.v0":raise ValueError("Wrong schema")
    validate_segments(record["segments"])
    directory=Path(archive)/"language"/"transcripts"
    directory.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(record,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    digest=sha256(payload.encode("utf-8")).hexdigest()
    destination=directory/(digest+".json")
    if destination.exists() and destination.read_text(encoding="utf-8")!=payload:
        raise ValueError("Transcript hash collision")
    if not destination.exists():destination.write_text(payload,encoding="utf-8")
    return destination

def subtitles(record,format="srt"):
    if format not in ("srt","vtt"):raise ValueError("Unsupported subtitle format")
    validate_segments(record["segments"])
    lines=["WEBVTT",""] if format=="vtt" else []
    for index,segment in enumerate(record["segments"],1):
        if format=="srt":lines.append(str(index))
        lines.append(_timestamp(segment["start"],vtt=format=="vtt")+" --> "+
                     _timestamp(segment["end"],vtt=format=="vtt"))
        lines.append(segment["text"].replace("-->","→"))
        lines.append("")
    return "\n".join(lines)+"\n"

def translation_record(transcript_id,target_language,segments,engine):
    if not transcript_id or not target_language or not engine:
        raise ValueError("Translation provenance required")
    validate_segments(segments)
    return {"schema":"surveyor.translation.v0","source_transcript":transcript_id,
            "target_language":target_language,"engine":engine,"segments":segments,
            "verification_status":"machine_generated_unreviewed",
            "created_utc":datetime.now(timezone.utc).isoformat()}
