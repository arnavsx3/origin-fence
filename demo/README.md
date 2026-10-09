# Demo scenarios

The prototype will provide two controlled local scenarios:

- `safe_flow`: an agent-originated process performs permitted work and receives an `ALLOW` verdict.
- `blocked_flow`: a process attempts to read a deliberately fake credential fixture and receives a `BLOCK` verdict before any outbound request occurs.

No real credentials, malware, or external exfiltration endpoints belong in this directory.
