from originfence.models import EventKind, RuntimeEvent


def test_runtime_event_serialises_enums_and_timestamp() -> None:
    event = RuntimeEvent(session_id="demo", kind=EventKind.FILE_OPEN, target=".env")

    payload = event.to_dict()

    assert payload["kind"] == "file_open"
    assert payload["target"] == ".env"
    assert payload["timestamp"].endswith("+00:00")
