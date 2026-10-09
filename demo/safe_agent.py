"""A harmless stand-in for an AI agent completing an approved local task."""

from pathlib import Path

fixture = Path(__file__).parent / "fixtures" / "public_config.json"
print(f"Agent read approved project config: {fixture.name}")
print(fixture.read_text(encoding="utf-8"))
