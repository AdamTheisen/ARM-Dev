import glob
import act
import numpy as np
from scipy import stats
import pandas as pd

#files = glob.glob('/data/archive/sgp/sgpsondewnpnC1.b1/*20230801*')

now = pd.Timestamp.now().to_period('m')
dates = pd.period_range('2001-04-01', now-1, freq='M').strftime('%Y%m').tolist()

bins = np.arange(0, 26000, 1000)
df = pd.DataFrame(columns=bins[:-1])
for d in dates:
    print(d)
    files = glob.glob('/data/archive/sgp/sgpsondewnpnC1.b1/*b1.' + d + '*')
    if len(files) <= 1:
        continue
    files.sort()
    try:
        ds = act.io.armfiles.read_netcdf(files, concat_dim='time', parallel=True)
        ds = ds.dropna(dim='time')
        bin_means, bin_edges, binnumber = stats.binned_statistic(ds['alt'].values, ds['wspd'].values, bins=bins)

        ts = pd.to_datetime(d)
        df.loc[ts] = bin_means
    except:
        print('Failing')
        continue

df.to_csv('data.csv')
