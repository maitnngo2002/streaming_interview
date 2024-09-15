import pytest
from . import weather

def test_sample_processing():
    events = [
        {"type": "sample", "stationName": "Foster", "timestamp": 1000, "temperature": 32.0},
        {"type": "sample", "stationName": "Foster", "timestamp": 2000, "temperature": 34.0},
        {"type": "sample", "stationName": "Montrose", "timestamp": 1500, "temperature": 33.0},
        {"type": "control", "command": "snapshot"}
    ]
    results = list(weather.process_events(events))
    assert len(results) == 1
    assert results[0] == {
        "type": "snapshot",
        "asOf": 2000,
        "stations": {
            "Foster": {"high": 34.0, "low": 32.0},
            "Montrose": {"high": 33.0, "low": 33.0}
        }
    }

def test_reset():
    events = [
        {"type": "sample", "stationName": "Foster", "timestamp": 1000, "temperature": 32.0},
        {"type": "control", "command": "reset"},
        {"type": "sample", "stationName": "Foster", "timestamp": 2000, "temperature": 34.0},
        {"type": "control", "command": "snapshot"}
    ]
    results = list(weather.process_events(events))
    assert len(results) == 2
    assert results[0] == {"type": "reset", "asOf": 1000}
    assert results[1] == {
        "type": "snapshot",
        "asOf": 2000,
        "stations": {
            "Foster": {"high": 34.0, "low": 34.0}
        }
    }

def test_unknown_message_type():
    events = [{"type": "unknown"}]
    with pytest.raises(ValueError, match="Unknown event type: unknown. Please verify input."):
        list(weather.process_events(events))

def test_unknown_command():
    events = [{"type": "control", "command": "unknown"}]
    with pytest.raises(ValueError, match="Unknown command: unknown. Please verify input."):
        list(weather.process_events(events))

def test_empty_input():
    events = []
    results = list(weather.process_events(events))
    assert len(results) == 0

def test_ignore_control_messages_when_no_data():
    events = [
        {"type": "control", "command": "snapshot"},
        {"type": "control", "command": "reset"},
        {"type": "sample", "stationName": "Foster", "timestamp": 1000, "temperature": 32.0},
        {"type": "control", "command": "snapshot"}
    ]
    results = list(weather.process_events(events))
    assert len(results) == 1
    assert results[0] == {
        "type": "snapshot",
        "asOf": 1000,
        "stations": {
            "Foster": {"high": 32.0, "low": 32.0}
        }
    }

def test_maintain_latest_timestamp():
    events = [
        {"type": "sample", "stationName": "Foster", "timestamp": 2000, "temperature": 32.0},
        {"type": "sample", "stationName": "Montrose", "timestamp": 1000, "temperature": 30.0},
        {"type": "control", "command": "snapshot"}
    ]
    results = list(weather.process_events(events))
    assert len(results) == 1
    assert results[0]["asOf"] == 2000

def test_handle_float_inf():
    events = [
        {"type": "control", "command": "snapshot"}
    ]
    results = list(weather.process_events(events))
    assert len(results) == 0