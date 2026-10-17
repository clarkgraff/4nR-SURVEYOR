"""Minimal command line for SURVEYOR development increment A."""
import argparse
import json
from pathlib import Path
from .core import JobStore, Mission, SUITES, Surveyor


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
    args = parser.parse_args()
    with_store = JobStore(Path(args.db))
    try:
        if args.command == "suites":
            print(json.dumps(SUITES, indent=2))
        elif args.command == "submit":
            print(with_store.submit(Mission(args.suite, args.question, args.scope)))
        elif args.command == "get":
            print(json.dumps(with_store.get(args.job_id), indent=2))
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
