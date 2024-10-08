from typing import Any, Iterable, Generator
from collections import defaultdict

def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    stations = defaultdict(lambda: {"high": float('-inf'), "low": float('inf')})
    latest_timestamp = 0
    has_data = False

    for event in events:
        event_type = event.get("type")

        if event_type == "sample":
            station_name = event["stationName"]
            temperature = event["temperature"]
            timestamp = event["timestamp"]

            latest_timestamp = max(latest_timestamp, timestamp)

            stations[station_name]["high"] = max(stations[station_name]["high"], temperature)
            stations[station_name]["low"] = min(stations[station_name]["low"], temperature)
            has_data = True

        elif event_type == "control":
            command = event.get("command")

            if command == "snapshot" and has_data:
                yield {
                    "type": "snapshot",
                    "asOf": latest_timestamp,
                    "stations": {
                        station: {
                            "high": data["high"],
                            "low": data["low"]
                        }
                        for station, data in stations.items()
                        if data["high"] != float('-inf') and data["low"] != float('inf')
                    }
                }
            elif command == "reset" and has_data:
                yield {
                    "type": "reset",
                    "asOf": latest_timestamp
                }
                stations.clear()
                latest_timestamp = 0
                has_data = False

            elif command not in ["snapshot", "reset"]:
                raise ValueError(f"Unknown command: {command}. Please verify input.")
        else:
            raise ValueError(f"Unknown event type: {event_type}. Please verify input.")