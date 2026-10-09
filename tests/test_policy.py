from originfence.models import EventKind, RuntimeEvent, Verdict
from originfence.policy import PolicyConfig, PolicyEngine


def make_engine() -> PolicyEngine:
    return PolicyEngine(
        PolicyConfig(
            protected_paths=["**/.aws/credentials", "**/.env"],
            allowed_hosts=["registry.npmjs.org"],
        )
    )


def test_blocks_a_protected_file_access() -> None:
    decision = make_engine().evaluate(
        RuntimeEvent("demo", EventKind.FILE_OPEN, target="/tmp/demo/.aws/credentials")
    )

    assert decision.verdict is Verdict.BLOCK
    assert "protected file" in decision.reason


def test_allows_an_allowlisted_destination() -> None:
    decision = make_engine().evaluate(
        RuntimeEvent("demo", EventKind.NETWORK_CONNECT, target="registry.npmjs.org:443")
    )

    assert decision.verdict is Verdict.ALLOW


def test_blocks_unknown_network_after_sensitive_access() -> None:
    engine = make_engine()
    engine.evaluate(RuntimeEvent("demo", EventKind.FILE_OPEN, target="/tmp/demo/.env"))

    decision = engine.evaluate(
        RuntimeEvent("demo", EventKind.NETWORK_CONNECT, target="example.invalid:443")
    )

    assert decision.verdict is Verdict.BLOCK
