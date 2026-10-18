"""D8B — optional FFprobe/FFmpeg media inspection and derived-audio extraction."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from .media import get_media, verify_media

def probe_media(archive: str | Path, digest: str, *, ffprobe="ffprobe") -> dict:
    original=get_media(archive,digest)
    if not verify_media(original):
        raise ValueError("Archive content hash mismatch")
    command=[ffprobe,"-v","error","-show_format","-show_streams","-of","json",
             original["content_path"]]
    result=subprocess.run(command,capture_output=True,text=True,timeout=120,check=True)
    if len(result.stdout)>2_000_000:
        raise ValueError("FFprobe metadata too large")
    streams=json.loads(result.stdout)
    return {"schema":"surveyor.media-probe.v0","source_sha256":digest,
            "streams":streams.get("streams",[]),"format":streams.get("format",{}),
            "verification_status":"technical_metadata_only"}

def extract_audio(archive: str | Path, digest: str, *, ffmpeg="ffmpeg") -> dict:
    original=get_media(archive,digest)
    if not verify_media(original):
        raise ValueError("Archive content hash mismatch")
    root=Path(archive)/"media"/"derivatives"
    root.mkdir(parents=True,exist_ok=True)
    destination=root/(digest+"-audio.wav")
    if destination.exists():
        return {"schema":"surveyor.media-derivative.v0","parent_sha256":digest,
                "path":str(destination),"sha256_hex":_digest(destination),
                "format":"pcm_s16le","sampling_rate_hz":16000,"channels":1}
    temp=root/(digest+"-audio.partial.wav")
    try:
        subprocess.run([ffmpeg,"-nostdin","-hide_banner","-loglevel","error","-n",
                        "-i",original["content_path"],"-map","0:a:0",
                        "-vn","-ac","1","-ar","16000","-c:a","pcm_s16le",
                        str(temp)],check=True,timeout=3600,capture_output=True)
        if not temp.exists() or not temp.stat().st_size:
            raise ValueError("No audio was extracted")
        temp.replace(destination)
    finally:
        temp.unlink(missing_ok=True)
    return {"schema":"surveyor.media-derivative.v0","parent_sha256":digest,
            "path":str(destination),"sha256_hex":_digest(destination),
            "format":"pcm_s16le","sampling_rate_hz":16000,"channels":1}

def _digest(path):
    h=sha256()
    with Path(path).open("rb") as stream:
        while chunk:=stream.read(1024*1024):
            h.update(chunk)
    return h.hexdigest()
