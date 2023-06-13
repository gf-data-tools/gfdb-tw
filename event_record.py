from datetime import datetime
from pathlib import Path

import hjson
import pandas as pd


class EventRecord:
    def __init__(self, event_file: Path | str):
        event_file = Path(event_file).resolve()
        event_data = hjson.loads(event_file.read_text())
        self.data: dict[pd.DataFrame] = {}
        for k, rec in event_data.items():
            df = pd.DataFrame.from_records(rec)
            df["start_time"] = pd.to_datetime(df["start_time"])
            df["end_time"] = df["start_time"].shift(
                -1, fill_value=datetime.now().replace(microsecond=0)
            )
            self.data[k] = df

    def get_event_info(self, target, identifier: int):
        df: pd.DataFrame = self.data[target].query(f"identifier=={identifier}")
        if not len(df):
            return None
        note = df.iloc[0]["note"]
        periods = (
            (
                r["start_time"].timestamp() - 3600 * 8,
                r["end_time"].timestamp() - 3600 * 8,
            )
            for _, r in df.iterrows()
        )
        query_cond = " or ".join(
            [f"({s:.0f}<dev_time and dev_time<{e:.0f})" for s, e in periods]
        )
        return note, query_cond

    def __getitem__(self, target):
        if target not in self.data:
            raise KeyError(target)
        return self.__iterator(target)

    def __iterator(self, target):
        i = 0
        while True:
            ret = self.get_event_info(target, i)
            if not ret:
                return
            yield ret
            i += 1


if __name__ == "__main__":
    event_record = EventRecord("events.hjson")
    for note, periods in event_record["gun_nm"]:
        print(note, periods)
