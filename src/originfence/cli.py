"""Command-line entry point for the OriginFence prototype."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from originfence.config import load_policy
from originfence.monitor import run_guarded_command
from originfence.policy import PolicyEngine
from originfence.store import EventStore


def build_parser() -> argparse.ArgumentParser:
    """Create the small command surface needed by the proof of concept."""
    parser = argparse.ArgumentParser(prog="originfence", description="Runtime guardrails for AI agents")
    subcommands = parser.add_subparsers(dest="command", required=True)

    run = subcommands.add_parser("run", help="run a command in a monitored session")
    run.add_argument("--policy", type=Path, required=True, help="YAML policy file")
    run.add_argument("--database", type=Path, default=Path("data/originfence.sqlite3"))
    run.add_argument("target", nargs=argparse.REMAINDER, help="command to execute after --")

    demo = subcommands.add_parser("demo", help="run a controlled local demo")
    demo.add_argument("scenario", choices=["safe", "blocked"])
    demo.add_argument("--database", type=Path, default=Path("data/originfence.sqlite3"))

    dashboard = subcommands.add_parser("dashboard", help="open the local event dashboard")
    dashboard.add_argument("--database", type=Path, default=Path("data/originfence.sqlite3"))
    dashboard.add_argument("--port", type=int, default=8000)
    return parser


def _demo_command(scenario: str) -> tuple[Path, list[str]]:
    root = Path(__file__).resolve().parents[2]
    policy = root / "demo" / "policy.yaml"
    script = root / "demo" / f"{scenario}_agent.py"
    return policy, [sys.executable, str(script)]


def _print_timeline(store: EventStore, session_id: str) -> None:
    print("\nOriginFence event timeline")
    print("=" * 72)
    for item in store.timeline(session_id):
        print(f"{item['kind']:18} {item['verdict'].upper():5}  {item['target'] or ''}")
        print(f"  {item['reason']}")


def main(argv: list[str] | None = None) -> None:
    """Run a guarded command or one of the project-owned demo scenarios."""
    arguments = build_parser().parse_args(argv)
    if arguments.command == "dashboard":
        import uvicorn

        from originfence.web import create_app

        uvicorn.run(create_app(arguments.database), host="127.0.0.1", port=arguments.port)
        return
    if arguments.command == "demo":
        policy_path, command = _demo_command(arguments.scenario)
    else:
        policy_path = arguments.policy
        command = arguments.target
        if command[:1] == ["--"]:
            command = command[1:]

    store = EventStore(arguments.database)
    policy = PolicyEngine(load_policy(policy_path))
    result = run_guarded_command(command, policy, store)
    _print_timeline(store, result.session_id)
    label = "BLOCKED" if result.blocked else "ALLOWED"
    print(f"\nVerdict: {label} | session={result.session_id} | observed_events={result.event_count}")
