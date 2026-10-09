from originfence.cli import _verdict_display


def test_verdict_display_has_clear_plain_text_when_not_a_tty(monkeypatch) -> None:
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)

    assert _verdict_display("block") == "✕ BLOCK"
