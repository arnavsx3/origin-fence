from originfence.cli import build_parser


def test_cli_accepts_blocked_demo() -> None:
    arguments = build_parser().parse_args(["demo", "blocked"])

    assert arguments.command == "demo"
    assert arguments.scenario == "blocked"
