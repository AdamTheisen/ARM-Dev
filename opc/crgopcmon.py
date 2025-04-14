import glob
import act
from datetime import datetime as dt
from datetime import timedelta
import numpy as np
import pandas as pd

today = dt.today().strftime('%Y%m%d')
yesterday = (dt.now() - timedelta(days=1)).strftime('%Y%m%d')

files = glob.glob('/data/datastream/crg/crgaosopcmonS2.00/*' + today + '*')
files.sort()
skip = np.arange(0,34)
skip = np.append(skip, [35, 36, 37, 38])
ds = act.io.read_csv(files, skiprows=skip, header=0, sep='\t')

time = [pd.to_datetime(ds['Date'].values[i]+'T'+ds['Time'].values[i]) for i in range(len(ds['Date'].values))]

ds['Time'].values = time
ds = ds.drop_vars('Time')
ds = ds.assign_coords({'index': time})
ds = ds.rename({'index': 'time'})

print(list(ds))
