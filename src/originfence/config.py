"""Loading and validation for local OriginFence policy files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from originfence.policy import PolicyConfig


class ConfigError(ValueError):
    """Raised when a policy file has an unsupported shape."""


def load_policy(path: Path) -> PolicyConfig:
    """Load the small YAML policy format used by the prototype."""
    try:
        content: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError as error:
        raise ConfigError(f"Could not read policy file: {path}") from error

    if not isinstance(content, dict):
        raise ConfigError("Policy root must be a YAML mapping.")

    protected_paths = content.get("protected_paths", [])
    network = content.get("network", {})
    if not isinstance(protected_paths, list) or not all(
        isinstance(item, str) for item in protected_paths
    ):
        raise ConfigError("protected_paths must be a list of strings.")
    if not isinstance(network, dict):
        raise ConfigError("network must be a mapping.")

    allowed_hosts = network.get("allowed_hosts", [])
    if not isinstance(allowed_hosts, list) or not all(isinstance(item, str) for item in allowed_hosts):
        raise ConfigError("network.allowed_hosts must be a list of strings.")

    return PolicyConfig(
        protected_paths=protected_paths,
        allowed_hosts=allowed_hosts,
        block_unknown_after_sensitive_access=bool(
            network.get("block_unknown_after_sensitive_access", True)
        ),
        block_unapproved_network=bool(network.get("block_unapproved_network", False)),
    )
