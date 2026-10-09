# Demo guide

Use this sequence for a clean OriginFence demonstration:

1. Start with `originfence demo safe` to show that the guard records approved work without blocking it.
2. Run `originfence demo blocked` to show that the local policy blocks an agent-originated read of `mock_credentials.txt`.
3. Run `originfence demo network-blocked` to show an unapproved outbound connection attempt being contained.
4. Start `originfence dashboard` and open `http://127.0.0.1:8000`.
5. Capture the runtime timeline containing the protected-file or network event and the process-tree stop verdict.

## What the demo proves

- The monitored command is launched in an isolated process session.
- OriginFence observes a real local file-open syscall through `strace`.
- OriginFence observes a real local network-connect syscall through `strace`.
- A deterministic YAML policy produces the blocking verdict.
- The guard terminates only the monitored process group.
- The decision and causal event timeline stay local in SQLite.
- The dashboard distinguishes all captured trace events from security-relevant events, so expected Python runtime activity does not obscure the proof.

## What it does not claim

- Kernel-level or cross-platform enforcement
- Coverage of agent processes that OriginFence did not launch
- Protection against every malicious dependency or plugin
- A replacement for sandboxing, dependency verification, or endpoint security
