"""Explicit multi-suite coordination with durable underlying jobs.

Research outputs are marked unverified until a separate evidence system checks them.
The caller, not an unconstrained model, approves the participating suites.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Callable
from .core import JobStore, Mission, lemonade_chat, utcnow
from .specialists import SPECIALISTS, system_prompt
from .evidence import from_inference

@dataclass(frozen=True)
class ResearchRequest:
    question: str
    suites: tuple[str, ...]
    approved_scope: str = ""

    def validate(self) -> None:
        if not self.question.strip():
            raise ValueError("Question is required")
        if not self.suites or len(self.suites) > len(SPECIALISTS):
            raise ValueError("Specify between one and six suites")
        if len(set(self.suites)) != len(self.suites):
            raise ValueError("Duplicate suite")
        if any(suite not in SPECIALISTS for suite in self.suites):
            raise ValueError("Unknown suite")

def run_research(store: JobStore, request: ResearchRequest,
                 infer: Callable[[str, str, str], dict] | None = None) -> dict:
    """Sequential jobs preserve results and failures in the existing SQLite store.

    A failure prevents further dispatch and returns a partial task report.
    """
    request.validate()
    if infer is None:
        def infer(suite: str, question: str, prompt: str) -> dict:
            return lemonade_chat(question, suite, system_instructions=prompt)
    results = []
    job_ids = []
    for suite in request.suites:
        job_id = store.submit(Mission(suite, request.question, request.approved_scope))
        job_ids.append(job_id)
        store.transition(job_id, "queued", "running")
        try:
            result = infer(suite, request.question, system_prompt(suite, request.approved_scope))
            if not isinstance(result, dict):
                raise TypeError("Inference adapter must return a dictionary")
            evidence = from_inference(suite, request.question, result).export()
            result = {**result, "suite": suite, "evidence_status": "unverified", "evidence_package": evidence}
            store.transition(job_id, "running", "completed", result=result)
            results.append({"job_id": job_id, "status": "completed", "result": result})
        except Exception as exc:
            store.transition(job_id, "running", "failed", error=str(exc))
            results.append({"job_id": job_id, "status": "failed", "error": str(exc)})
            break
    return {
        "schema": "surveyor.research-batch.v0",
        "created_utc": utcnow(),
        "suites_requested": list(request.suites),
        "job_ids": job_ids,
        "status": ("completed" if len(results) == len(request.suites)
                   and all(x["status"] == "completed" for x in results)
                   else "partial_failure"),
        "research_outputs": results,
        "review_status": "not_reviewed",
        "note": "No retrieval, scholarly evidence checking or NERDS integration is implemented.",
    }
