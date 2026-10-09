"""A controlled demonstration of a suspicious agent-originated child action."""

from pathlib import Path
import time

fixture = Path(__file__).parent / "fixtures" / "mock_credentials.txt"
print("Agent child process attempting to inspect a protected demo fixture.")
fixture.read_text(encoding="utf-8")

# OriginFence should terminate this monitored process before this delay ends.
time.sleep(3)
