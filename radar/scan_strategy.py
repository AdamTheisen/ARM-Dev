import glob
import act
import numpy as np

files = glob.glob('/data/datastream/nsa/nsaxsaprcfrC1.a1/*.20250904*')
files.sort()
for f in files:
    ds = act.io.read_arm_netcdf(f)
    sm = ds.attrs['scan_mode']
    time = (ds['time'].values[-1] - ds['time'].values[0]).astype('timedelta64[s]')
    if sm == 'rhi':
        print(sm, time, np.unique(np.round(ds['azimuth'].values, decimals=0)))
    elif sm == 'ppi':
        print(sm, time, np.unique(np.round(ds['elevation'].values, decimals=0)))
    elif sm == 'vpt':
        print(sm, time)
    ds.close()
