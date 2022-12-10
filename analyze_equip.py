import json
import pandas as pd
import gf_utils
from gf_utils.stc_data import get_stc_data
from pathlib import Path
from datetime import datetime
from collections import defaultdict

 # %% Equip log
log_dir = Path('../elisa/logs/equip')
output_file = Path('equip.csv')
if output_file.exists():
    full_record_df = pd.read_csv(output_file).set_index('id',drop=False)
    last_record = full_record_df['file'].max()
    last_id = full_record_df['id'].max()
else:
    full_record_df = pd.DataFrame()
    last_record = '000000-000000.json'
    last_id = 0

begin_ts = int(datetime(2022,10,28,10).timestamp())

records = [full_record_df]
for record_file in sorted(log_dir.iterdir()):
    if record_file.name <= last_record:
        continue
    last_record = record_file.name
    print(last_record, end='\r')
    record_df = pd.read_json(record_file,orient='records',convert_dates=False).query(f'quality_lv==0 and dev_time>{begin_ts} and id>{last_id}').sort_values(by='id').set_index('id',drop=False)
    if len(record_df)==0:
        continue
    last_id = record_df['id'].max()
    record_df['file'] = last_record
    record_df['trust'] = False
    counter = defaultdict(int)
    for i,record in record_df[::-1].iterrows():
        counter[record['equip_id']]+=1
        record_df.at[i,'trust'] = True
        if counter[record['equip_id']] >= 10:
            break
    records.append(record_df)
full_record_df = pd.concat(records)

full_record_df.to_csv(output_file,index=False,line_terminator='\n')

# %% Gun-nm
log_dir = Path('../elisa/logs/gun_nm')
gamedata = get_stc_data('../GF_Data_Tools/data/ch/formatted/json')
output_file = Path('gun_nm.csv')
if output_file.exists():
    full_record_df = pd.read_csv(output_file).set_index('id',drop=False)
    last_record = full_record_df['file'].max()
    last_id = full_record_df['id'].max()
else:
    full_record_df = pd.DataFrame()
    last_record = '000000-000000.json'
    last_id = 0

begin_ts = int(datetime(2022,10,28,10).timestamp())

records = [full_record_df]
for record_file in sorted(log_dir.iterdir()):
    if record_file.name <= last_record:
        continue
    last_record = record_file.name
    print(last_record, end='\r')
    record_df = pd.read_json(record_file,orient='records',convert_dates=False).query(f'id>{last_id}').sort_values(by='id').set_index('id',drop=False)
    if len(record_df)==0:
        continue
    last_id = record_df['id'].max()
    record_df['file'] = last_record
    record_df['trust_2'] = False
    record_df['trust_3'] = False
    record_df['trust_4'] = False
    record_df['trust_5'] = False
    for level in range(2,6):
        counter = defaultdict(int)
        for i,record in record_df[::-1].iterrows():
            gun_id = record['gun_id']
            if gamedata['gun'][gun_id]['rank']>=level:
                counter[gun_id]+=1
                record_df.at[i,f'trust_{level}'] = True
                if counter[gun_id] >= 10:
                    break
    records.append(record_df)
full_record_df = pd.concat(records)

full_record_df.to_csv(output_file,index=False,line_terminator='\n')