from app.websocket_manager import ws_manager


def test_event_signature_verification():
    event_id = "evt-123"
    timestamp = 1739810000
    event_type = "flush"

    signature = ws_manager.generate_event_signature(event_id, timestamp, event_type)
    assert ws_manager.verify_event_signature(event_id, timestamp, event_type, signature)


def test_event_signature_rejects_tampering():
    event_id = "evt-123"
    timestamp = 1739810000
    signature = ws_manager.generate_event_signature(event_id, timestamp, "flush")

    assert not ws_manager.verify_event_signature(event_id, timestamp + 1, "flush", signature)
