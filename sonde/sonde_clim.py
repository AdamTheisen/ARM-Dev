import glob
import act
import numpy as np
from scipy import stats
import pandas as pd
import dask


def proc_data(f, variables):
    try:
        ds = act.io.armfiles.read_netcdf(f, parallel=True)
        ds = ds[variables]
        ds = ds.dropna(dim='time')
        data = {}
        for v in variables:
            data[v] = ds[v].values
    except:
        print('Error with ' + f)
        for v in variables:
            data[v] = -9999
    return data

#files = glob.glob('/data/archive/sgp/sgpsondewnpnC1.b1/*20230801*')

now = pd.Timestamp.now().to_period('m')
dates = pd.period_range('2001-04-01', now-1, freq='M').strftime('%Y%m').tolist()


bins = np.arange(0, 26000, 500)
variables = ['alt', 'wspd', 'tdry', 'rh']
for d in dates:
    print(d)
    files = glob.glob('/data/archive/sgp/sgpsondewnpnC1.b1/*b1.' + d + '*')
    if len(files) <= 1:
        continue
    files.sort()
    task = []
    for f in files:
        task.append(dask.delayed(proc_data)(f, variables))
    results = dask.compute(*task)

    # Get data from dict
    dat = {}
    for v in variables:
        dat[v] = []    
        dat['time'] = []
    for r1 in results:
        if len(r1) <= 1:
            print('Results Error with' + f)
            continue
        for v in variables:
            dat[v] = np.concatenate([data[v], r1[v]])
    print(dat)
    bin_data = {}
    for v in variables + ['time', 'count']:
        bin_data[v] = []
    try:
        ts = pd.to_datetime(d, format='%Y%m')
        bin_data['time'] = np.concatenate([data['time'], ts])
        bin_data['count'] = np.concatenate([data['count'], len(files)])
        print(bin_data)
        sys.exit()
        for v in variables:
            bin_means, bin_edges, bin_number = stats.binned_statistic(dat['alt'], dat[v], bins=bins)
        
    except:
        print('Stats Error with ' + f)
        continue
