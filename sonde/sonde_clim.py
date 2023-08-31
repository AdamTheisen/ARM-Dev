import glob
import act
import numpy as np
from scipy import stats
import pandas as pd
import dask
import xarray as xr


def proc_data(f, variables):
    data = {}
    try:
        ds = act.io.armfiles.read_netcdf(f, parallel=True)
        ds = ds[variables]
        old_ds = ds
        ds = ds.dropna(dim='time')
        for v in variables:
            data[v] = ds[v].values
    except:
        print('Error with ' + f)
        for v in variables:
            data[v] = [-9999]
    return data

#files = glob.glob('/data/archive/sgp/sgpsondewnpnC1.b1/*20230801*')

now = pd.Timestamp.now().to_period('m')
dates = pd.period_range('2001-04-01', now-1, freq='M').strftime('%Y%m').tolist()


bins = np.arange(0, 26000., 500.)
variables = ['alt', 'wspd', 'tdry', 'rh', 'dp', 'u_wind', 'v_wind', 'asc', 'pres']

bin_data = {}
for v in ['time', 'count']:
    bin_data[v] = {'data': [], 'dims': ['time']}
for v in variables:
    bin_data[v] = {'data': [], 'dims': ['time', 'height']}
bin_data['height'] = {'data': bins[0:-1], 'dims': ['height']}

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
    ct = 0
    for r1 in results:
        if len(r1['alt']) <= 1:
            print('Results Error')
            continue
        ct += 1
        for v in variables:
            dat[v] = np.concatenate([dat[v], r1[v]])
    
    try:
        ts = pd.to_datetime(d, format='%Y%m')
        bin_data['time']['data'] = np.concatenate([bin_data['time']['data'], [ts]])
        bin_data['count']['data'] = np.concatenate([bin_data['count']['data'], [ct]])

        for v in variables[0:]:
            bin_means, bin_edges, bin_number = stats.binned_statistic(dat['alt'], dat[v], bins=bins)
            if len(bin_data[v]['data']) == 0:
                bin_data[v]['data'] = bin_means
            else:
                bin_data[v]['data'] = np.vstack([bin_data[v]['data'], bin_means])
    except:
        print('Stats Error with ' + f)
        continue

ds = xr.Dataset.from_dict(bin_data)
ds.to_netcdf('sgpsondeC1.b1.nc')
