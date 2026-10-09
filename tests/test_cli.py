from originfence.cli import build_parser


def test_cli_accepts_blocked_demo() -> None:
    arguments = build_parser().parse_args(["demo", "blocked"])

    assert arguments.command == "demo"
    assert arguments.scenario == "blocked"


def test_cli_accepts_dashboard_port() -> None:
    arguments = build_parser().parse_args(["dashboard", "--port", "9090"])

    assert arguments.command == "dashboard"
    assert arguments.port == 9090
