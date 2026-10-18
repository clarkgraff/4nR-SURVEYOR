"""D8A — explicit, permission-gated local media archive.

No downloads from arbitrary pages or streaming services. Remote acquisition
adapters must be implemented separately with explicit permission checks.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import mimetypes
import os
from pathlib import Path
import shutil
import tempfile

EXTENSIONS = frozenset({".mp4",".mov",".mkv",".webm",".mp3",".wav",".flac",".m4a",".aac",".ogg",".opus",".aiff",".aif"})
MAX_MEDIA_BYTES = 20 * 1024**3

@dataclass(frozen=True)
class MediaRecord:
    schema: str
    sha256_hex: str
    byte_count: int
    original_name: str
    content_path: str
    source_url: str | None
    licence_basis: str
    operator: str
    acquired_utc: str
    media_type: str
    verification_status: str = "not_verified"

def import_media(source: str | Path, archive: str | Path, *, operator: str,
                 licence_basis: str, source_url: str | None = None,
                 max_bytes: int = MAX_MEDIA_BYTES) -> dict:
    if not operator.strip() or not licence_basis.strip():
        raise ValueError("Operator and explicit permission/licence basis required")
    path=Path(source)
    if path.is_symlink() or not path.is_file() or path.suffix.lower() not in EXTENSIONS:
        raise ValueError("Unsupported, missing or symbolic-link media source")
    stat=path.stat()
    if not 0 < stat.st_size <= max_bytes:
        raise ValueError("Invalid media size")
    if source_url is not None and not source_url.startswith("https://"):
        raise ValueError("Source URL must be HTTPS")
    root=Path(archive)/"media"
    root.mkdir(parents=True,exist_ok=True)
    digest=sha256()
    count=0
    with tempfile.NamedTemporaryFile(dir=root,prefix=".media-",delete=False) as tmp:
        temporary=Path(tmp.name)
        try:
            with path.open("rb") as stream:
                while chunk:=stream.read(1024*1024):
                    count+=len(chunk)
                    if count>max_bytes:
                        raise ValueError("Media exceeds size limit")
                    digest.update(chunk)
                    tmp.write(chunk)
            tmp.flush()
            os.fsync(tmp.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    fingerprint=digest.hexdigest()
    destination=root/(fingerprint+path.suffix.lower())
    if destination.exists():
        if _hash_file(destination)!=fingerprint:
            temporary.unlink(missing_ok=True)
            raise ValueError("Existing archive media hash mismatch")
        temporary.unlink()
    else:
        temporary.replace(destination)
    record=MediaRecord("surveyor.media.v0",fingerprint,count,path.name,str(destination),
                       source_url,licence_basis,operator,datetime.now(timezone.utc).isoformat(),
                       mimetypes.guess_type(path.name)[0] or "application/octet-stream")
    with (root/"media-events.jsonl").open("a",encoding="utf-8") as log:
        log.write(json.dumps(asdict(record),ensure_ascii=False)+"\n")
    return asdict(record)

def _hash_file(path: Path) -> str:
    value=sha256()
    with path.open("rb") as stream:
        while data:=stream.read(1024*1024):
            value.update(data)
    return value.hexdigest()

def verify_media(record: dict) -> bool:
    return _hash_file(Path(record["content_path"]))==record["sha256_hex"]

def get_media(archive: str | Path, digest: str) -> dict:
    if len(digest)!=64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise ValueError("Invalid media identifier")
    log=Path(archive)/"media"/"media-events.jsonl"
    if not log.exists():
        raise KeyError(digest)
    for line in reversed(log.read_text(encoding="utf-8").splitlines()):
        record=json.loads(line)
        if record["sha256_hex"]==digest:
            return record
    raise KeyError(digest)
