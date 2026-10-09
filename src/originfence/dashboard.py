"""Streamlit dashboard entry point for the OriginFence proof of concept."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import streamlit as st

from originfence.store import EventStore


def parse_arguments() -> argparse.Namespace:
    """Read the database location forwarded by the OriginFence CLI."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--database", type=Path, default=Path("data/originfence.sqlite3"))
    arguments, _ = parser.parse_known_args()
    return arguments


def meaningful_events(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Hide interpreter noise while retaining demo and policy-relevant events."""
    return [
        event
        for event in events
        if event["verdict"] != "allow"
        or event["kind"] != "file_open"
        or "/demo/" in str(event.get("target", ""))
    ]


def render() -> None:
    """Render the local, presentation-ready event dashboard."""
    arguments = parse_arguments()
    store = EventStore(arguments.database)
    events = meaningful_events(store.timeline())
    blocked = [event for event in events if event["verdict"] == "block"]

    st.set_page_config(page_title="OriginFence", page_icon="🛡️", layout="wide")
    st.title("OriginFence")
    st.caption("Local runtime guardrails for AI coding agents")
    st.markdown(
        "Trace what an AI agent causes, then enforce policy before a risky process chain escapes the machine."
    )

    left, centre, right = st.columns(3)
    left.metric("Observed events", len(events))
    centre.metric("Blocked actions", len(blocked), delta="Contained" if blocked else None)
    right.metric("Evidence storage", "Local SQLite")

    st.divider()
    header, refresh = st.columns([5, 1])
    header.subheader("Runtime timeline")
    if refresh.button("Refresh", use_container_width=True):
        st.rerun()

    if not events:
        st.info("Run `originfence demo blocked` to generate a controlled protected-file event.")
        return

    for event in events:
        verdict = str(event["verdict"]).upper()
        color = {"ALLOW": "🟢", "ASK": "🟡", "BLOCK": "🔴"}.get(verdict, "⚪")
        target = event.get("target") or "—"
        with st.expander(f"{color} {verdict} · {event['kind'].replace('_', ' ')} · {target}"):
            st.write(event["reason"])
            st.json(
                {
                    "session_id": event["session_id"],
                    "pid": event["pid"],
                    "target": target,
                    "timestamp": event["timestamp"],
                },
                expanded=False,
            )


if __name__ == "__main__":
    render()
