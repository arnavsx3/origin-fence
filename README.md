# OriginFence

**Runtime guardrails for AI coding agents**

OriginFence traces what an AI agent causes on a developer machine and blocks unsafe action chains before sensitive data leaves the device.

> Guard the chain, not just the command.

## The problem

AI coding agents can run commands, install dependencies, read project files, and access the network. A command that appears harmless can spawn child processes that access credentials or make unexpected outbound connections.

Existing permission prompts approve an initial action. OriginFence follows its consequences:

```text
AI agent → command → child process → sensitive file → network connection
```

## What OriginFence does

- Launches an AI-agent session inside a monitored process tree
- Tracks command execution, file access, and outbound connection attempts
- Identifies agent-originated descendant processes
- Applies deterministic policy rules: `ALLOW`, `ASK`, or `BLOCK`
- Stops a risky process tree and records the causal chain
- Displays local, explainable security events in a dashboard

## Prototype scope

This repository contains a Linux proof of concept focused on one end-to-end scenario:

1. An agent-originated process starts.
2. A child script attempts to access a protected file such as `.aws/credentials`, `.env`, or an SSH key.
3. OriginFence detects the access.
4. The policy engine blocks the process before an unapproved outbound connection can occur.
5. The dashboard shows the complete event chain and verdict.

The prototype is designed for demonstration and research. It is not a replacement for endpoint security, dependency verification, sandboxing, or vendor security updates.

## Planned architecture

```text
Agent launcher
    ↓
Runtime tracer
    ↓
Event normalizer
    ↓
Policy engine
    ↓
Enforcement service
    ↓
SQLite event store + local dashboard
```

## Planned stack

- Python 3.11
- FastAPI and WebSockets
- SQLite
- `strace` for prototype syscall tracing
- `psutil` for process-tree management
- YAML policy files
- HTML, CSS, and JavaScript dashboard

## Repository layout

```text
src/originfence/       Guard engine: monitoring, policy, enforcement, storage, web
config/                Example policy rules
demo/                  Controlled safe and blocked scenarios
docs/                  Architecture and prototype boundaries
tests/                 Automated checks for policy and event handling
```

## Demo policy

```yaml
protected_paths:
  - "~/.aws/*"
  - "~/.ssh/*"
  - "**/.env"

network:
  allow:
    - "registry.npmjs.org"
  block_unknown_after_sensitive_access: true
```

## Status

🚧 Active hackathon prototype

## Team

Built by the OriginFence team for AI-Manthan 2.0.
