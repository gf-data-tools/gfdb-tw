from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import *

import hjson


@dataclass(init=False)
class Event:
    start_time: datetime
    end_time: datetime
    note: str

    def __init__(self: Event, start_time: str, end_time: str, note: str):
        self.note = note
        self.start_time = datetime.fromisoformat(start_time)
        self.end_time = datetime.fromisoformat(end_time)


@dataclass
class Period:
    times: Iterable[tuple[datetime]] = field(default_factory=list)
    note: str = ""

    @property
    def query(self: Period) -> str:
        return " or ".join(
            f"({s.timestamp():.0f}<dev_time and dev_time<{e.timestamp():.0f})"
            for s, e in self.times
        )


class EventRecord:
    def __init__(self, file: str | Path) -> None:
        self.data = hjson.loads(Path(file).read_text())

    def __getitem__(self, key: str) -> list[Period]:
        data = self.data[key]
        events = [Event(**x) for x in data]
        timestamps = sorted(
            set.union({x.start_time for x in events}, {x.end_time for x in events})
        )
        periods = defaultdict(Period)
        for start, end in zip(timestamps[:-1], timestamps[1:]):
            key_id = []
            note = None
            for i, event in enumerate(events):
                if start >= event.start_time and end <= event.end_time:
                    key_id.append(i)
                    note = event.note
            periods[tuple(key_id)].note = note
            periods[tuple(key_id)].times.append((start, end))
        assert len(periods) == len({x.note for x in periods.values()})
        periods = sorted(periods.values(), key=lambda x: x.times[-1][0])
        return periods


if __name__ == "__main__":
    event_record = EventRecord("event.hjson")
    for k in ["gun_nm", "gun_sp", "equip", "fairy"]:
        print(k)
        for period in event_record[k]:
            print(period.note, period.query)
