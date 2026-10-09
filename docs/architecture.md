# Prototype architecture

OriginFence is intentionally built as a narrow, local proof of concept.
It proves that a process launched from an AI-agent session can be traced,
evaluated against deterministic rules, and stopped with an explainable record.

```text
agent command
    │
    ▼
session launcher ──► runtime monitor ──► normalised events
                                             │
                                             ▼
                                      policy engine
                                             │
                     ┌───────────────────────┴───────────────────────┐
                     ▼                                               ▼
                allow / record                                 block / stop tree
                     │                                               │
                     └───────────────────────┬───────────────────────┘
                                             ▼
                                  SQLite event store + Streamlit dashboard
```

## Prototype boundary

The first working slice supports a process started by OriginFence on Linux.
It records descendant process activity, checks protected-file access, applies a
YAML policy, stops the process tree on a blocking verdict, and exposes the
result in a local dashboard.

It does not claim to provide kernel-level enforcement, universal AI-agent
coverage, or a substitute for endpoint detection and response tooling.
