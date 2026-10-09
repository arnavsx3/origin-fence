from originfence.cli import _demo_command, build_parser


def test_cli_accepts_blocked_demo() -> None:
    arguments = build_parser().parse_args(["demo", "blocked"])

    assert arguments.command == "demo"
    assert arguments.scenario == "blocked"


def test_cli_accepts_dashboard_port() -> None:
    arguments = build_parser().parse_args(["dashboard", "--port", "9090"])

    assert arguments.command == "dashboard"
    assert arguments.port == 9090


def test_network_demo_maps_to_python_module_name() -> None:
    _, command = _demo_command("network-blocked")

    assert command[-1].endswith("network_blocked_agent.py")
