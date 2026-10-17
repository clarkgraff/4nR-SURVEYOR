"""Minimal command line for SURVEYOR development increment A."""
import argparse
import json
from pathlib import Path
from .core import JobStore, Mission, SUITES, Surveyor
from .orchestrator import ResearchRequest, run_research
from .pipeline import PipelineRequest, run_pipeline
from .discovery import DiscoveryRequest, discover, save_report, SOURCES
from .discovery_connectors import manifest_connector
from .youtube_connector import youtube_connector
from .presentation import present, save_presentation, record_decision, ACTIONS
from .handoff import create_handoff, execute_handoff
from .knowledge import KnowledgeCatalogue


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
    discovery.add_argument("--manifest", help="Local JSON candidate manifest")
    discovery.add_argument("--live", action="store_true", help="Use official YouTube API (requires SURVEYOR_YOUTUBE_API_KEY)")
    discovery.add_argument("--archive", default="surveyor-archive")
    discovery.add_argument("--scope", default="")
    discovery.add_argument("--limit", type=int, default=20)
    presentation = sub.add_parser("present")
    presentation.add_argument("discovery_file")
    presentation.add_argument("--pipeline-result", help="Optional saved pipeline JSON results")
    presentation.add_argument("--archive", default="surveyor-archive")
    decision = sub.add_parser("decide")
    decision.add_argument("presentation_file")
    decision.add_argument("item", type=int)
    decision.add_argument("action", choices=sorted(ACTIONS))
    decision.add_argument("--operator", required=True)
    decision.add_argument("--reason", required=True)
    decision.add_argument("--archive", default="surveyor-archive")
    handoff = sub.add_parser("handoff", help="Create queued job from recorded investigation decision")
    handoff.add_argument("presentation_file")
    handoff.add_argument("item", type=int)
    handoff.add_argument("--reason", required=True)
    handoff.add_argument("--archive", default="surveyor-archive")
    followup = sub.add_parser("run-handoff", help="Run queued follow-up without autonomous downloads")
    followup.add_argument("job_id", type=int)
    followup.add_argument("--reviewer", choices=SUITES)
    followup.add_argument("--archive", default="surveyor-archive")
    knowledge = sub.add_parser("knowledge-add", help="D7 curate approved discovery candidate")
    knowledge.add_argument("presentation_file")
    knowledge.add_argument("item", type=int)
    knowledge.add_argument("--archive", default="surveyor-archive")
    knowledge.add_argument("--knowledge-db", default="surveyor-knowledge.sqlite3")
    query_knowledge = sub.add_parser("knowledge-search")
    query_knowledge.add_argument("query")
    query_knowledge.add_argument("--knowledge-db", default="surveyor-knowledge.sqlite3")
    gui = sub.add_parser("gui", help="D8 local review GUI")
    gui.add_argument("--archive", default="surveyor-archive")
    gui.add_argument("--knowledge-db", default="surveyor-knowledge.sqlite3")
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
            if args.live and args.manifest:
                parser.error("Choose --live or --manifest, not both")
            if not args.live and not args.manifest:
                parser.error("Supply --manifest or --live")
            if args.live:
                if args.provider != "youtube":
                    parser.error("Live connector currently supported only for youtube")
                connector = youtube_connector()
            else:
                connector = manifest_connector(args.manifest, args.provider)
            report = discover(request, {args.provider: connector})
            destination = save_report(report, args.archive)
            report["archive_path"] = str(destination)
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif args.command == "present":
            research = None
            if args.pipeline_result:
                research = json.loads(Path(args.pipeline_result).read_text(encoding="utf-8-sig"))
            report = present(args.discovery_file, pipeline_result=research)
            destination = save_presentation(report, args.archive)
            report["presentation_path"] = str(destination)
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif args.command == "decide":
            result = record_decision(args.presentation_file, args.item, args.action,
                                     args.operator, args.reason, archive=args.archive)
            if args.action == "investigate_further":
                result["handoff"] = create_handoff(with_store, args.presentation_file, args.item,
                                                    args.reason, archive=args.archive)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "handoff":
            outcome = create_handoff(with_store, args.presentation_file, args.item,
                                     args.reason, archive=args.archive)
            print(json.dumps(outcome, indent=2, ensure_ascii=False))
        elif args.command == "run-handoff":
            outcome = execute_handoff(with_store, args.job_id,
                                      reviewer=args.reviewer, archive=args.archive)
            print(json.dumps(outcome, indent=2, ensure_ascii=False))
        elif args.command == "knowledge-add":
            cat = KnowledgeCatalogue(args.knowledge_db)
            try:
                print(json.dumps(cat.add(args.presentation_file, args.item, args.archive),
                                 indent=2, ensure_ascii=False))
            finally:
                cat.close()
        elif args.command == "knowledge-search":
            cat = KnowledgeCatalogue(args.knowledge_db)
            try:
                print(json.dumps(cat.search(args.query), indent=2, ensure_ascii=False))
            finally:
                cat.close()
        elif args.command == "gui":
            from .gui import launch_gui
            launch_gui(args.archive, args.knowledge_db)
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
