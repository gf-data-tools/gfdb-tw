import sqlite3

import pandas as pd
from gf_utils2.gamedata.gamedata import special_keys
from gf_utils.stc_data import get_stc_data

gamedata = get_stc_data(
    ["../GF_Data_Tools/data/ch/stc", "../GF_Data_Tools/data/ch/catchdata"],
    "../GF_Data_Tools/data/ch/asset/table",
)
with sqlite3.connect("../Elisa/logs/develop_log.db") as con:
    for k in gamedata:
        print(k)
        if not gamedata[k]:
            continue
        if isinstance(gamedata[k], list):
            data = pd.DataFrame(gamedata[k], index=special_keys.get(k, "id"))
        else:
            data = pd.DataFrame(gamedata[k].values())
        idx_key = special_keys.get(k, "id")
        data.to_sql(k, con, if_exists="replace", index=False)
