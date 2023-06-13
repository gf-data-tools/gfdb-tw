import sqlite3
from pathlib import Path

import pandas as pd

path = Path("../Elisa/logs/develop_log.db").resolve()
conn = sqlite3.connect(f"file://{path}?immutable=1", uri=True)
data = pd.read_sql("select * from equip", conn)
data.sort_values(["dev_time", "sub_table", "id"]).to_csv(
    "records/equip.csv", index=False
)
data = pd.read_sql("select * from gun_nm", conn)
data.sort_values(["dev_time", "sub_table", "id"]).to_csv(
    "records/gun_nm.csv", index=False
)
data = pd.read_sql("select * from gun_sp", conn)
data.sort_values(["dev_time", "sub_table", "id"]).to_csv(
    "records/gun_sp.csv", index=False
)
