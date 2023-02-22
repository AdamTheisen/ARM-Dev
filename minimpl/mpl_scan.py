import sys
#sys.path.insert(0,'/Users/atheisen/Code/sandbox/ACT')

import matplotlib
matplotlib.use('Agg')

import act
import matplotlib.pyplot as plt
import glob
import pyart
import numpy as np
import xarray as xr
import os
import dask
import datetime as dt


files = glob.glob('/data/datastream/sgp/sgpmplS01.00/*')
files.sort()
tasks = []
t1 = dt.datetime.now() - dt.timedelta(minutes=61)

mfiles = []
for f in files:
    st = os.stat(f)
    mtime = dt.datetime.fromtimestamp(st.st_mtime)
    if mtime > t1:
        mfiles.append(f)
files = mfiles

if len(files) == 0:
    raise ValueError
sdate = files[0].split('.')[-2][0:8]
edate = files[-1].split('.')[-2][0:8]
dates = act.utils.datetime_utils.dates_between(sdate,edate)

ap = '/home/theisen/test/minimpl/MMPL5005_Afterpulse_201503312000.bin'
dt = '/home/theisen/test/minimpl/MMPL5005_SPCM23721_Deadtime11.bin'
op = '/home/theisen/test/minimpl/MMPL5005_Overlap_SigmaMPL_201504041700.bin'

for d in dates:
    fdate = d.strftime('%Y%m%d')
    dfile = glob.glob('/data/datastream/sgp/sgpmplS01.00/*raw.'+fdate+'*')

    for f in dfile:
        try:
            mpl = act.io.mpl.read_sigma_mplv5(f, afterpulse=ap, dead_time=dt, overlap=op)
        except:
            continue
        az = mpl['azimuth_angle'].values
        el = mpl['elevation_angle'].values
        ftime = f.split('.')[-2]
        if np.unique(el)[0] == 0 and np.unique(az)[0] == 0:
            continue

        ratio = mpl['nrb_crosspol'].values/(mpl['nrb_crosspol'].values + mpl['nrb_copol'].values) * 100.
        long_name = 'Depolarization Ratio (cross/(co+cross) * 100.'
        attrs = {'long_name': long_name, 'units': ' '}
        mpl['depol'] = xr.DataArray(ratio, coords=mpl['nrb_copol'].coords, attrs=attrs)    

        if len(np.unique(el)) < len(np.unique(az)):
           sweep = np.zeros(len(mpl['azimuth_angle']))
           diff = abs(np.diff(el))
           index = np.where(diff >= 1)[0]
           if len(index) == 0:
               sweep_start = np.array([0])
               sweep_end = np.array([len(el)])
           else:
               sweep_start = np.insert(index,0,0)
               sweep_end = np.append(index-1,len(el),len(el)-1)
           ct  =  0
           for i in range(len(sweep_start)):
               sweep[slice(sweep_start[i],sweep_end[i],1)]  = ct
               ct += 1
           attrs = {'long_name': 'sweep', 'units': ' '}
           mpl['sweep'] = xr.DataArray(sweep, coords=mpl['elevation_angle'].coords, attrs=attrs)    
           scan = 'ppi'
           dmin = 0
           dmax = 1
        else:
           sweep = np.zeros(len(mpl['azimuth_angle']))
           diff = abs(np.diff(az))
           index = np.where(diff > 0)[0]
           sweep_start = np.insert(index,0,0)
           sweep_end = np.append(index-1,len(az),len(az)-1)
           ct  =  0
           for i in range(len(sweep_start)):
               sweep[slice(sweep_start[i],sweep_end[i]+1,1)]  = ct
               ct += 1
           attrs = {'long_name': 'sweep', 'units': ' '}
           mpl['sweep'] = xr.DataArray(sweep, coords=mpl['elevation_angle'].coords, attrs=attrs)    
           scan = 'rhi'
           dmin = None
           dmax = None

        outfile = '/home/theisen/www/minimpl/data/'+scan+'/sgpminimplS01.00.'+ftime+'.nc'
        mpl = mpl.drop('time_utc')
        mpl.to_netcdf(outfile)

        mpl = mpl.fillna(0)
        radar = act.utils.create_pyart_obj(mpl, azimuth='azimuth_angle', elevation='elevation_angle',
                                           range_var='range', sweep='sweep', sweep_mode=scan)
        display = pyart.graph.RadarDisplay(radar)
        display.plot('nrb_copol', sweep=0,title_flag=False, vmin=dmin, vmax=dmax,cmap='jet')
        filename = 'sgpminimplS01.00.'+ftime+'.png'
        print('Saving to '+filename)
        plt.savefig('/home/theisen/www/minimpl/images/'+scan+'/'+filename)
        mpl.close()
        plt.clf()



