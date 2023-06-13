import sqlite3
from pathlib import Path

import pandas as pd
from gf_utils.stc_data import get_stc_data

from event_record import EventRecord

gamedata = get_stc_data(
    ["../GF_Data_Tools/data/ch/stc", "../GF_Data_Tools/data/ch/catchdata"],
    "../GF_Data_Tools/data/ch/asset/table",
)
eventrecord = EventRecord("./events.hjson")
path = Path("../Elisa/logs/develop_log.db").resolve()
conn = sqlite3.connect(f"file://{path}?immutable=1", uri=True)


def analyze_gun_nm(full_record: pd.DataFrame):
    formula_series = []
    for formula in gamedata["recommended_formula"].values():
        if formula["develop_type"] != 1 or formula["name"] == "人形混合":
            continue
        record = full_record.query(
            f"(mp=={formula['mp']} and "
            f"ammo=={formula['ammo']} and "
            f"mre=={formula['mre']} and "
            f"part=={formula['part']})"
        )
        r = {
            i: record.query(f"trust_{i}==True")["gun_rank"].value_counts(
                normalize=True
            )[i]
            for i in range(2, 6)
        }
        p = 1
        s = {i: p - (p := p - p * r[i]) for i in range(2, 6)}
        record = record.query(
            " or ".join([f"(gun_rank=={i} and trust_{i}==True)" for i in range(2, 6)])
        )
        record: pd.Series = record.groupby(["mp", "ammo", "mre", "part", "gun_rank"])[
            "gun_id"
        ].value_counts(normalize=True)
        for i in range(2, 6):
            record[record.index.get_level_values("gun_rank") == i] *= s[i]
        formula_series.append(record)
    return pd.concat(formula_series)


if __name__ == "__main__":
    gun_nm = pd.read_sql("select * from gun_nm", conn)
    event_df = []
    for note, time_query in eventrecord["gun_nm"]:
        full_records = gun_nm.query(time_query)
        # print(note, time_query)
        if len(full_records) == 0:
            continue
        r = analyze_gun_nm(full_records)
        print(note, len(full_records))
        event_df.append(r.rename(note))
    event_df = pd.concat(event_df, axis=1)
    event_df = event_df.fillna(0)
    event_df["gun_name"] = event_df.index.get_level_values("gun_id").map(
        lambda i: gamedata["gun"][i]["name"]
    )
    event_df = event_df.set_index("gun_name", append=True)
    event_df = event_df.sort_values(note, ascending=False).sort_index(
        level=["part", "mp", "ammo", "mre", "gun_rank"], kind="", sort_remaining=False
    )
    event_df.to_excel("gun_nm.xlsx")
