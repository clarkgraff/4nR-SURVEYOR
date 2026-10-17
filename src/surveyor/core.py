"""Dependency-free SURVEYOR job registry, persistence and dispatch foundation.

This is not a navigation engine or a deployed specialist research system.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import sqlite3
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen

SUITES = {
    "CHEKOV": "Navigation, weather, currents & voyage intelligence",
    "EMERSON": "Music & ethnomusicology",
    "BOURDAIN": "Cuisine & foodways",
    "CHAKOTAY": "Culture, history, archaeology, anthropology & languages",
    "GOODALL": "Biology, ecology, oceanography & environmental science",
    "HADID": "Architecture, engineering & built heritage",
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Mission:
    suite: str
    question: str
    approved_scope: str = ""

    def validate(self) -> None:
        if self.suite not in SUITES:
            raise ValueError(f"Unknown suite: {self.suite}")
        if not self.question.strip():
            raise ValueError("Mission question cannot be empty")


class JobStore:
    """Persistent, explicitly dispatched jobs. No autonomous background execution."""

    def __init__(self, database: str | Path):
        self.connection = sqlite3.connect(str(database))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suite TEXT NOT NULL,
            question TEXT NOT NULL,
            approved_scope TEXT NOT NULL,
            status TEXT NOT NULL,
            created_utc TEXT NOT NULL,
            modified_utc TEXT NOT NULL,
            result_json TEXT,
            error TEXT
        )""")
        self.connection.commit()

    def submit(self, mission: Mission) -> int:
        mission.validate()
        now = utcnow()
        cursor = self.connection.execute(
            "INSERT INTO jobs (suite, question, approved_scope, status, created_utc, modified_utc) VALUES (?,?,?,?,?,?)",
            (mission.suite, mission.question, mission.approved_scope, "queued", now, now),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, job_id: int) -> dict:
        row = self.connection.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return dict(row)

    def transition(self, job_id: int, expected: str, status: str, *, result: dict | None = None, error: str | None = None) -> None:
        cursor = self.connection.execute(
            "UPDATE jobs SET status=?,modified_utc=?,result_json=?,error=? WHERE id=? AND status=?",
            (status, utcnow(), json.dumps(result) if result is not None else None, error, job_id, expected),
        )
        self.connection.commit()
        if cursor.rowcount != 1:
            raise ValueError(f"Job {job_id} is not in state {expected}")

    def cancel(self, job_id: int) -> None:
        self.transition(job_id, "queued", "cancelled")

    def resume(self, job_id: int) -> None:
        self.transition(job_id, "cancelled", "queued")

    def close(self) -> None:
        self.connection.close()


def lemonade_chat(question: str, suite: str, *, endpoint: str | None = None,
                  model: str | None = None, timeout: float = 120,\n                  system_instructions: str | None = None) -> dict:
    """OpenAI-compatible adapter; verify endpoint/model on installed Lemonade release."""
    endpoint = (endpoint or os.environ.get("SURVEYOR_LEMONADE_URL", "http://127.0.0.1:13305/api/v1")).rstrip("/")
    model = model or os.environ.get("SURVEYOR_MODEL")
    if not model:
        raise RuntimeError("Set SURVEYOR_MODEL to the installed Lemonade model identifier")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instructions or ("You are SURVEYOR-" + suite + ". Work only within the supplied approved scope. Mark uncertain claims and provide source provenance. Do not issue navigational commands or alter NERDS state.")},
            {"role": "user", "content": question},
        ],
        "stream": False,
    }
    req = Request(endpoint + "/chat/completions", json.dumps(payload).encode("utf-8"),
                  {"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=timeout) as response:
        raw = json.load(response)
    content = raw["choices"][0]["message"]["content"]
    return {"suite": suite, "model": model, "response": content,
            "source_status": "unverified_model_response", "timestamp_utc": utcnow()}


class Surveyor:
    def __init__(self, store: JobStore, executor: Callable[[str, str], dict] | None = None):
        self.store = store
        self.executor = executor or (lambda suite, question: lemonade_chat(question, suite))

    def dispatch(self, job_id: int) -> dict:
        job = self.store.get(job_id)
        self.store.transition(job_id, "queued", "running")
        try:
            result = self.executor(job["suite"], job["question"])
            self.store.transition(job_id, "running", "completed", result=result)
        except Exception as exc:
            self.store.transition(job_id, "running", "failed", error=str(exc))
            raise
        return result
