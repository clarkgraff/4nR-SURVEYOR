"""Minimal command line for SURVEYOR development increment A."""
import argparse
import json
from pathlib import Path
from .core import JobStore, Mission, SUITES, Surveyor
from .orchestrator import ResearchRequest, run_research
from .pipeline import PipelineRequest, run_pipeline
from .discovery import DiscoveryRequest, discover, save_report, SOURCES
from .discovery_connectors import manifest_connector


def main():
    parser = argparse.ArgumentParser(description="4nR-SURVEYOR parent runtime (development)")
    parser.add_argument("--db", default="surveyor.sqlite3", help="SQLite persistence path")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("suites")
    add = sub.add_parser("submit")
    add.add_argument("suite", choices=SUITES)
    add.add_argument("question")
    add.add_argument("--scope", default="")
    one = sub.add_parser("get")
    one.add_argument("job_id", type=int)
    for action in ("run", "cancel", "resume"):
        cmd = sub.add_parser(action)
        cmd.add_argument("job_id", type=int)
    multi = sub.add_parser("research", help="Explicit sequential dispatch across selected suites")
    multi.add_argument("question")
    multi.add_argument("--suites", nargs="+", required=True, choices=SUITES)
    multi.add_argument("--scope", default="")
    pipeline = sub.add_parser("pipeline", help="D4 explicit research pipeline")
    pipeline.add_argument("suite", choices=SUITES)
    pipeline.add_argument("question")
    pipeline.add_argument("--scope", default="")
    pipeline.add_argument("--archive", default="surveyor-archive")
    pipeline.add_argument("--source", action="append", default=[])
    pipeline.add_argument("--approve-host", action="append", default=[])
    pipeline.add_argument("--reviewer", choices=SUITES)
    pipeline.add_argument("--vet", action="store_true", help="Run parent vetting against approved source passages")
    pipeline.add_argument("--allow-download", action="store_true")
    discovery = sub.add_parser("discover", help="D6A offline source discovery")
    discovery.add_argument("suite", choices=SUITES)
    discovery.add_argument("query")
    discovery.add_argument("--provider", required=True, choices=sorted({p for values in SOURCES.values() for p in values}))
    discovery.add_argument("--manifest", required=True, help="Local JSON candidate manifest")
    discovery.add_argument("--archive", default="surveyor-archive")
    discovery.add_argument("--scope", default="")
    discovery.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    with_store = JobStore(Path(args.db))
    try:
        if args.command == "suites":
            print(json.dumps(SUITES, indent=2))
        elif args.command == "submit":
            print(with_store.submit(Mission(args.suite, args.question, args.scope)))
        elif args.command == "get":
            print(json.dumps(with_store.get(args.job_id), indent=2))
        elif args.command == "research":
            report = run_research(with_store, ResearchRequest(args.question, tuple(args.suites), args.scope))
            print(json.dumps(report, indent=2))
        elif args.command == "pipeline":
            if args.source and not args.allow_download:
                parser.error("--source requires --allow-download")
            if args.allow_download and not args.source:
                parser.error("--allow-download requires --source")
            request = PipelineRequest(args.suite, args.question, args.scope,
                        tuple(args.source), frozenset(args.approve_host), args.reviewer, args.vet)
            request.validate()
            report = run_pipeline(with_store, request, Path(args.archive))
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif args.command == "discover":
            request = DiscoveryRequest(args.suite, args.query, (args.provider,),
                                       args.scope, args.limit)
            report = discover(request, {args.provider: manifest_connector(args.manifest, args.provider)})
            destination = save_report(report, args.archive)
            report["archive_path"] = str(destination)
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif args.command == "run":
            print(json.dumps(Surveyor(with_store).dispatch(args.job_id), indent=2))
        elif args.command == "cancel":
            with_store.cancel(args.job_id)
        elif args.command == "resume":
            with_store.resume(args.job_id)
    finally:
        with_store.close()


if __name__ == "__main__":
    main()
