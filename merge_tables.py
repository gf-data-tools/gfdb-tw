from pathlib import Path

import pandas as pd

log_dir = Path(R"../Elisa/logs/")
table_names = ["equip", "fairy", "gun_nm", "gun_sp"]

for fname in table_names:
    tables = []
    for fp in log_dir.glob(f"*/{fname}.csv"):
        table_id = int(fp.parent.name[-1])
        df = pd.read_csv(fp)
        df["table"] = table_id
        tables.append(df.set_index(["table", "id"]))
    table = pd.concat(tables).sort_values("dev_time", kind="mergesort")
    table.to_csv(f"records/{fname}.csv")
