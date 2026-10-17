"""Bounded, explicitly authorised HTTPS source acquisition.

No general-purpose URL fetching from model output. Domains must be approved by
the operator and HTTPS redirects are rejected. Retrieved does not mean reviewed.
For deployments allowing arbitrary hosts, use an outbound policy/proxy as well.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import ipaddress
import json
from pathlib import Path
import socket
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_BYTES = 2_000_000
ALLOWED_TYPES = ("text/plain", "text/html", "application/json")
USER_AGENT = "4nR-SURVEYOR-research/0.1"

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Redirects are not authorised")

def _approved_url(url: str, approved_hosts: frozenset[str]) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only HTTPS URLs without credentials are allowed")
    host = parsed.hostname.lower().rstrip(".")
    if parsed.port not in (None, 443) or host not in approved_hosts:
        raise ValueError("Host or port is not explicitly authorised")
    if parsed.fragment:
        raise ValueError("Fragments are not accepted in source acquisition")
    return host

def _public_dns(host: str) -> None:
    """Defence in depth. Also enforce network egress restrictions in deployment."""
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    if not addresses:
        raise ValueError("No DNS addresses")
    for info in addresses:
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global:
            raise ValueError("Non-public destination is forbidden")

@dataclass(frozen=True)
class Acquisition:
    url: str
    sha256_hex: str
    byte_count: int
    media_type: str
    acquired_utc: str
    review_status: str = "retrieved_not_reviewed"

def fetch_source(url: str, archive: str | Path, *, approved_hosts: frozenset[str],
                 max_bytes: int = MAX_BYTES, opener=None, dns_check=_public_dns) -> Acquisition:
    host = _approved_url(url, approved_hosts)
    if max_bytes < 1 or max_bytes > MAX_BYTES:
        raise ValueError("Invalid download limit")
    dns_check(host)
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": ", ".join(ALLOWED_TYPES)})
    client = opener if opener is not None else build_opener(_NoRedirect())
    try:
        with client.open(request, timeout=15) as response:
            final_url = response.geturl()
            if final_url != url:
                raise ValueError("Unexpected final URL")
            status = getattr(response, "status", 200)
            if status != 200:
                raise ValueError("Unexpected HTTP status")
            kind = response.headers.get_content_type().lower()
            if kind not in ALLOWED_TYPES:
                raise ValueError("Unsupported media type")
            declared = response.headers.get("Content-Length")
            if declared is not None and int(declared) > max_bytes:
                raise ValueError("Source exceeds limit")
            payload = response.read(max_bytes + 1)
    except HTTPError as exc:
        raise ValueError(f"Source HTTP error {exc.code}") from exc
    if len(payload) > max_bytes:
        raise ValueError("Source exceeds limit")
    fingerprint = sha256(payload).hexdigest()
    root = Path(archive)
    root.mkdir(parents=True, exist_ok=True)
    # Immutable per-content payload; metadata is a separate append-only event.
    blob = root / (fingerprint + ".source")
    if blob.exists():
        if sha256(blob.read_bytes()).hexdigest() != fingerprint:
            raise ValueError("Stored source hash mismatch")
    else:
        with blob.open("xb") as output:
            output.write(payload)
    event = Acquisition(url, fingerprint, len(payload), kind, datetime.now(timezone.utc).isoformat())
    with (root / "acquisitions.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
    return event
