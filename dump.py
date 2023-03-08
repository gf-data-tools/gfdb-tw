import sqlite3

import pandas as pd

conn = sqlite3.connect("../Elisa/logs/develop_log.db")
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
