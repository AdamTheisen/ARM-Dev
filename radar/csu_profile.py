import act
#import pyart
import glob
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime as dt
import warnings
import radtraq


warnings.filterwarnings("ignore", category=DeprecationWarning) 

today = dt.date.today().strftime("%Y%m%d")
yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime("%Y%m%d")
now = dt.datetime.now()
ago = now-dt.timedelta(minutes=60)
fdate = today

files = glob.glob('/data/datastream/guc/gucxprecipradarS2.00/*csu.sail-' + today + '*_PPI.nc')
yfiles = glob.glob('/data/datastream/guc/gucxprecipradarS2.00/*csu.sail-' + yesterday + '*_PPI.nc')
files += yfiles
files.sort()

for i, f in enumerate(files):
    if '_1_PPI' not in f:
        continue
    stat = os.stat(f)
    mtime = dt.datetime.fromtimestamp(stat.st_mtime)
    #if mtime < ago:
    #    continue

    f_comp = f.split('_')[0].split('-')
    fdate = str(f_comp[-2])
    ftime = (f_comp[-1])
    f_comp = f.split('.')[-2].split('_')
    scan_info = '_'.join([f_comp[-1], f_comp[-2]]) 

    obj = xr.open_dataset(f)
    prof = radtraq.proc.extract_profile_at_lat_lon(obj,38.95616, -106.9879, variables='DBZ',
               lat_name_in_obj='latitude', lon_name_in_obj='longitude', azimuth_range=0.5)
    height = [prof['height'].values[0]]
    time = [prof['time'].values[0]]
    data = {'DBZ': [float(prof['DBZ'].values[0])]}
    atts = prof['DBZ'].attrs
    obj.close()
    j = 1
    while '_1_PPI' not in files[i + j]:
        obj = xr.open_dataset(files[i + j])
        prof = radtraq.proc.extract_profile_at_lat_lon(obj,38.95616, -106.9879, variables='DBZ',
                   lat_name_in_obj='latitude', lon_name_in_obj='longitude', azimuth_range=0.5)
        height.append(prof['height'].values[0])
        data['DBZ'].append(float(prof['DBZ'].values))
        j += 1
        obj.close()

    obj = xr.Dataset()
    da = xr.DataArray([data['DBZ']], coords={'time': time, 'height': height}, dims=['time', 'height'],
                      attrs=atts)
    obj['DBZ'] = da

    nc_file = '/data/home/theisen/qme/guc/gucxprecipradarS2.00/gucxprecipradarS2.00.'+fdate+'.'+ftime+'.nc'
    obj.to_netcdf(nc_file)
