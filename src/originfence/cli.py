"""Command-line entry point for the OriginFence prototype."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from originfence.config import load_policy
from originfence.models import is_security_relevant
from originfence.monitor import run_guarded_command
from originfence.policy import PolicyEngine
from originfence.store import EventStore

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"


def build_parser() -> argparse.ArgumentParser:
    """Create the small command surface needed by the proof of concept."""
    parser = argparse.ArgumentParser(prog="originfence", description="Runtime guardrails for AI agents")
    subcommands = parser.add_subparsers(dest="command", required=True)

    run = subcommands.add_parser("run", help="run a command in a monitored session")
    run.add_argument("--policy", type=Path, required=True, help="YAML policy file")
    run.add_argument("--database", type=Path, default=Path("data/originfence.sqlite3"))
    run.add_argument("target", nargs=argparse.REMAINDER, help="command to execute after --")

    demo = subcommands.add_parser("demo", help="run a controlled local demo")
    demo.add_argument("scenario", choices=["safe", "blocked", "network-blocked"])
    demo.add_argument("--database", type=Path, default=Path("data/originfence.sqlite3"))

    dashboard = subcommands.add_parser("dashboard", help="open the Streamlit event dashboard")
    dashboard.add_argument("--database", type=Path, default=Path("data/originfence.sqlite3"))
    dashboard.add_argument("--port", type=int, default=8000)
    return parser


def _demo_command(scenario: str) -> tuple[Path, list[str]]:
    root = Path(__file__).resolve().parents[2]
    policy = root / "demo" / "policy.yaml"
    script = root / "demo" / f"{scenario.replace('-', '_')}_agent.py"
    return policy, [sys.executable, str(script)]


def _style(text: str, *codes: str) -> str:
    """Add terminal colour only when the caller can render it."""
    if not sys.stdout.isatty():
        return text
    return f"{''.join(codes)}{text}{_RESET}"


def _verdict_display(verdict: str) -> str:
    """Return a compact verdict label for the security timeline."""
    labels = {
        "allow": ("✓ ALLOW", _GREEN),
        "ask": ("? ASK", _YELLOW),
        "block": ("✕ BLOCK", _RED),
    }
    label, colour = labels[verdict]
    return _style(label, _BOLD, colour)


def _print_timeline(store: EventStore, session_id: str) -> int:
    """Print a concise, presentation-ready incident timeline."""
    visible_events = []
    for item in store.timeline(session_id):
        if not is_security_relevant(item["kind"], item["target"], item["verdict"]):
            continue
        visible_events.append(item)

    print(f"\n{_style('🛡  ORIGINFENCE INCIDENT REPORT', _BOLD, _CYAN)}")
    print(_style("─" * 68, _DIM))
    print(f"Session  {session_id}")
    print(f"Timeline {len(visible_events)} security-relevant actions")
    print(_style("─" * 68, _DIM))
    for number, item in enumerate(visible_events, start=1):
        action = item["kind"].replace("_", " ").title()
        target = item["target"] or "—"
        print(f"{number:02d}  {_verdict_display(str(item['verdict']))}  {action}")
        print(f"    {_style(str(target), _BOLD)}")
        print(f"    {_style(str(item['reason']), _DIM)}")

    return len(visible_events)


def main(argv: list[str] | None = None) -> None:
    """Run a guarded command or one of the project-owned demo scenarios."""
    arguments = build_parser().parse_args(argv)
    if arguments.command == "dashboard":
        dashboard = Path(__file__).resolve().parents[1] / "originfence" / "dashboard.py"
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    str(dashboard),
                    "--server.address",
                    "127.0.0.1",
                    "--server.port",
                    str(arguments.port),
                    "--server.headless=true",
                    "--browser.gatherUsageStats=false",
                    "--",
                    "--database",
                    str(arguments.database),
                ],
                check=False,
                env={
                    **os.environ,
                    "STREAMLIT_SERVER_HEADLESS": "true",
                    "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
                },
            )
        except KeyboardInterrupt:
            print("\nOriginFence dashboard stopped.")
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
    visible_event_count = _print_timeline(store, result.session_id)
    label = "BLOCKED" if result.blocked else "ALLOWED"
    label_colour = _RED if result.blocked else _GREEN
    action = "Monitored process group terminated" if result.blocked else "No containment action required"
    print(_style("─" * 68, _DIM))
    print(
        f"{_style('FINAL VERDICT', _BOLD)}  {_style(label, _BOLD, label_colour)}\n"
        f"Evidence       {result.captured_event_count} trace events captured · "
        f"{visible_event_count} security-relevant\n"
        f"Containment    {action}"
    )


if __name__ == "__main__":
    main()
