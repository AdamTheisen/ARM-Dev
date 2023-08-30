import glob
import act
import numpy as np
from scipy import stats
import pandas as pd
import dask


def proc_data(f):
    try:
        ds = act.io.armfiles.read_netcdf(f, parallel=True)
        ds = ds[['alt', 'wspd']] 
        ds = ds.dropna(dim='time')
        alt = ds['alt'].values
        wspd = ds['wspd'].values
    except:
        print('Error with ' + f)
        alt = [-9999.]
        wspd = [-9999.]
    return alt, wspd

#files = glob.glob('/data/archive/sgp/sgpsondewnpnC1.b1/*20230801*')

now = pd.Timestamp.now().to_period('m')
dates = pd.period_range('2010-03-01', now-1, freq='M').strftime('%Y%m').tolist()


bins = np.arange(0, 26000, 1000)
for d in dates:
    df = pd.DataFrame(columns=bins[:-1])
    print(d)
    files = glob.glob('/data/archive/sgp/sgpsondewnpnC1.b1/*b1.' + d + '*')
    if len(files) <= 1:
        continue
    files.sort()
    task = []
    for f in files:
        task.append(dask.delayed(proc_data)(f))
    results = dask.compute(*task)
    alt = []
    wspd = []
    for r1, r2 in results:
        if len(r1) <= 1:
            print('Results Error with' + f)
            continue
        alt = np.concatenate([alt, r1])
        wspd = np.concatenate([wspd, r2])
    bin_means, bin_edges, binnumber = stats.binned_statistic(alt, wspd, bins=bins)
    try:
        bin_means, bin_edges, binnumber = stats.binned_statistic(alt, wspd, bins=bins)
        ts = pd.to_datetime(d, format='%Y%m')
        df.loc[ts] = bin_means
    except:
        print('Stats Error with ' + f)
        continue
    df.to_csv('data.csv', mode='a')
