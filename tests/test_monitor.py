from originfence.models import EventKind
from originfence.monitor import parse_strace_line


def test_parses_openat_event() -> None:
    event = parse_strace_line(
        "demo", '1420  openat(AT_FDCWD, "/tmp/demo/.env", O_RDONLY) = 3'
    )

    assert event is not None
    assert event.kind is EventKind.FILE_OPEN
    assert event.pid == 1420
    assert event.target == "/tmp/demo/.env"


def test_parses_connect_event() -> None:
    event = parse_strace_line(
        "demo",
        '1420  connect(3, {sa_family=AF_INET, sin_port=htons(443), sin_addr=inet_addr("127.0.0.1")}, 16) = 0',
    )

    assert event is not None
    assert event.kind is EventKind.NETWORK_CONNECT
    assert event.target == "127.0.0.1"


def test_ignores_unrelated_syscalls() -> None:
    assert parse_strace_line("demo", "1420  close(3) = 0") is None
