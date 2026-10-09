# OriginFence

> **Runtime guardrails for AI coding agents**

[![CI](https://github.com/arnavsx3/origin-fence/actions/workflows/ci.yml/badge.svg)](https://github.com/arnavsx3/origin-fence/actions/workflows/ci.yml)

**OriginFence traces what an AI agent causes on a developer machine and blocks unsafe action chains before sensitive data leaves the device.**

```text
AI agent → command → child process → sensitive file → network connection
```

> Guard the chain, not just the command.

## Why it matters

AI coding agents can install dependencies, run shell commands, read project files, and connect to the network. An approval for one action does not automatically explain or constrain every process that action launches afterward.

OriginFence adds a local runtime checkpoint. It follows an agent-originated process chain, applies deterministic policy, and records an explainable verdict.

## What it proves

| Capability | Prototype behaviour |
| --- | --- |
| Agent-origin awareness | Launches the monitored command in its own process session |
| Runtime visibility | Observes `exec`, file-open, and connection syscalls with `strace` |
| Explainable policy | Evaluates YAML rules as `ALLOW`, `ASK`, or `BLOCK` |
| Scoped containment | Stops only the monitored process group on a blocking verdict |
| Local evidence | Stores the causal event timeline in SQLite |
| Presentation-ready view | Shows verdicts and event details in a Streamlit dashboard |

## The demo

The repository includes two controlled local scenarios:

- **Safe flow**: an agent-originated process reads a public project configuration and receives an `ALLOW` verdict.
- **Blocked flow**: an agent-originated process attempts to read a deliberately fake credential fixture. OriginFence detects the access, blocks it, and terminates the monitored process tree.

No real credentials, malware, or external exfiltration endpoint are used.

## Architecture

```text
Agent command
    │
    ▼
OriginFence launcher
    │
    ▼
strace runtime monitor ──► normalised events ──► YAML policy engine
                                                       │
                                      ┌────────────────┴────────────────┐
                                      ▼                                 ▼
                                  ALLOW / ASK                     BLOCK + stop tree
                                      │                                 │
                                      └───────────────┬─────────────────┘
                                                      ▼
                                       SQLite evidence + Streamlit dashboard
```

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'

# Record an approved local action
.venv/bin/originfence demo safe

# Record and contain a protected-file access
.venv/bin/originfence demo blocked

# Inspect the event timeline
.venv/bin/originfence dashboard
```

Open the dashboard at `http://127.0.0.1:8000`.

## Project layout

```text
src/originfence/     Runtime monitor, policy engine, enforcement, storage, dashboard
config/              Example policy rules
demo/                Safe and blocked proof scenarios with fake fixtures
docs/                Architecture and demo guidance
tests/               Automated policy, runtime, dashboard, and CLI checks
```

## Prototype boundary

OriginFence is a Linux proof of concept built for demonstration and research. It protects only processes it launches and does not claim to replace dependency verification, sandboxing, EDR, or vendor security updates.

## Team

Built by the OriginFence team for **AI-Manthan 2.0**.
