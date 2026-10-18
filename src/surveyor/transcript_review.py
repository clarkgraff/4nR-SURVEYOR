"""D8C-2 immutable transcript corrections, independent of the original machine output."""
from __future__ import annotations
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from .language import validate_segments

def corrected_transcript(original_path, changes, *, operator, reason, archive):
    original_path=Path(original_path)
    raw=original_path.read_bytes()
    original=json.loads(raw.decode("utf-8-sig"))
    if original.get("schema") not in ("surveyor.transcript.v0","surveyor.transcript-revision.v0"):
        raise ValueError("Not a transcript")
    if not operator.strip() or not reason.strip() or not changes:
        raise ValueError("Operator, reason and corrections required")
    updated=[dict(segment) for segment in original["segments"]]
    applied=[]
    for index,text in changes.items():
        if not isinstance(index,int) or index<0 or index>=len(updated):
            raise ValueError("Invalid segment index")
        if not isinstance(text,str) or not text.strip():
            raise ValueError("Correction cannot be blank")
        old=updated[index]["text"]
        if old==text:continue
        updated[index]["text"]=text
        applied.append({"index":index,"previous":old,"replacement":text})
    if not applied:raise ValueError("No changes to record")
    validate_segments(updated)
    record={"schema":"surveyor.transcript-revision.v0",
            "parent_sha256":sha256(raw).hexdigest(),
            "parent_path":str(original_path),
            "media_sha256":original["media_sha256"],
            "language":original["language"],
            "segments":updated,"corrections":applied,
            "operator":operator,"reason":reason,
            "verification_status":"human_corrected_not_fact_verified",
            "created_utc":datetime.now(timezone.utc).isoformat()}
    body=json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    digest=sha256(body.encode("utf-8")).hexdigest()
    destination=Path(archive)/"language"/"revisions"/(digest+".json")
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists() and destination.read_text(encoding="utf-8")!=body:
        raise ValueError("Revision hash collision")
    if not destination.exists():destination.write_text(body,encoding="utf-8")
    return destination
