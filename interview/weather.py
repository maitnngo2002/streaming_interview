from typing import Any, Iterable, Generator
from collections import defaultdict

def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    stations = defaultdict(lambda: {"high": float('-inf'), "low": float('inf')})
    latest_timestamp = 0

    for event in events:
        if event["type"] == "sample":
            station_name = event["stationName"]
            temperature = event["temperature"]
            timestamp = event["timestamp"]

            latest_timestamp = max(latest_timestamp, timestamp)

            stations[station_name]["high"] = max(stations[station_name]["high"], temperature)
            stations[station_name]["low"] = min(stations[station_name]["low"], temperature)