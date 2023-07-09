# %%
import sqlite3
from pathlib import Path

import pandas as pd
from gf_utils.stc_data import get_stc_data

from event_record import EventRecord

gamedata = get_stc_data(
    ["../GF_Data_Tools/data/ch/stc", "../GF_Data_Tools/data/ch/catchdata"],
    "../GF_Data_Tools/data/ch/asset/table",
)
eventrecord = EventRecord("./event.hjson")
path = Path("../elisa/logs/develop_log.db").resolve()
s = str(path).replace("\\", "/")
conn = sqlite3.connect(f"file:///{s}?immutable=1", uri=True)

gun_sp = pd.read_sql("select * from gun_sp", conn)


# %%
def analyze_gun_sp(full_records: pd.DataFrame):
    formula_series = {}
    formula_count = full_records.query("trust_2==True").value_counts(
        ["mp", "ammo", "mre", "part", "input_level"]
    )
    filtered = formula_count[formula_count > 2000].keys()
    if len(filtered) == 0:
        filtered = formula_count[formula_count == formula_count.max()].keys()
    for mp, ammo, mre, part, input_level in filtered:
        record = full_records.query(
            "mp==@mp and ammo==@ammo and mre==@mre and "
            "part==@part and input_level==@input_level"
        )
        r = record.query(f"trust_2==True")["gun_rank"].value_counts(normalize=True)
        formula_series[((mp, ammo, mre, part, input_level), "rank", "总数据")] = len(
            record.query(f"trust_2==True")
        )
        for i in range(2, 6):
            rank_record = record.query(f"gun_rank==@i and trust_{i}==True")
            if len(rank_record) == 0:
                continue
            formula_series[((mp, ammo, mre, part, input_level), "rank", i)] = r[i]
            formula_series[
                ((mp, ammo, mre, part, input_level), f"rank{i}", "总数据")
            ] = len(rank_record)
            res = rank_record["gun_id"].value_counts(normalize=True)
            for k, v in res.items():
                formula_series[
                    (
                        (mp, ammo, mre, part, input_level),
                        f"rank{i}",
                        gamedata["gun"][k]["name"],
                    )
                ] = (
                    v * r[i]
                )
    d = pd.Series(formula_series, dtype=float)
    return d


# %%
event_df = []
final_note = None
for period in eventrecord["gun_sp"]:
    note = period.note
    time_query = period.query
    full_records = gun_sp.query(time_query)
    # print(note, time_query)
    if len(full_records) == 0:
        continue
    final_note = note
    r = analyze_gun_sp(full_records)
    event_df.append(r.rename(note))
event_df = pd.concat(event_df, axis=1)

# %%
event_df.index.rename(["formula", "type", "target"], inplace=True)

# %%
event_df.sort_values(final_note, inplace=True, ascending=False)
event_df.sort_index(
    kind="stable",
    key=lambda col: col.map(lambda x: 0)
    if col.name == "target"
    else col.map(lambda col: (col[4], col[0] + col[1] + col[2] + 3 * col[3], col))
    if col.name == "formula"
    else col,
    inplace=True,
)


# %%
import numpy as np

style = event_df.style
gmap = np.log10(event_df)
gmap[gmap > 0] = np.nan
style.background_gradient(vmin=-3, vmax=0, cmap="gist_rainbow", gmap=gmap, axis=None)
style.applymap(
    lambda x: "background-color: white;color:black"
    if pd.isnull(x) or x % 1 == 0
    else ""
)


def formatter(v):
    if v > 1:
        return f"{v:.0f}"
    return f"{v:.4%}"


style.format(formatter, na_rep="")
style.to_html("gun_sp.html", table_uuid="0", sparse_index=False, sparse_columns=False)
# %%
