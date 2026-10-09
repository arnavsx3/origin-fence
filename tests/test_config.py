from pathlib import Path

import pytest

from originfence.config import ConfigError, load_policy


def test_load_policy_reads_example_shape(tmp_path: Path) -> None:
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        "protected_paths:\n  - '**/.env'\nnetwork:\n  allowed_hosts: [registry.npmjs.org]\n"
    )

    config = load_policy(policy_file)

    assert config.protected_paths == ["**/.env"]
    assert config.allowed_hosts == ["registry.npmjs.org"]


def test_load_policy_rejects_non_mapping(tmp_path: Path) -> None:
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text("- unexpected\n")

    with pytest.raises(ConfigError):
        load_policy(policy_file)
