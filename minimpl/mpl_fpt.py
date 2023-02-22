import sys
#sys.path.insert(0,'/Users/atheisen/Code/sandbox/ACT')

import matplotlib
matplotlib.use('Agg')

import act
import matplotlib.pyplot as plt
import glob
#import pyart
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

    mpl = []
    for f in dfile:
        obj = act.io.mpl.read_sigma_mplv5(f, afterpulse=ap, dead_time=dt, overlap=op)
        az = obj['azimuth_angle'].values
        el = obj['elevation_angle'].values
        if np.unique(el)[0] == 0 and np.unique(az)[0] == 0:
            mpl.append(obj)

    mpl = xr.merge(mpl)

    az = mpl['azimuth_angle'].values
    el = mpl['elevation_angle'].values
    ratio = mpl['nrb_crosspol'].values/(mpl['nrb_crosspol'].values + mpl['nrb_copol'].values) * 100.
    long_name = 'Depolarization Ratio (cross/(co+cross) * 100.'
    attrs = {'long_name': long_name, 'units': ' '}
    mpl['depol'] = xr.DataArray(ratio, coords=mpl['nrb_copol'].coords, attrs=attrs)    


    filename = 'sgpminimplS01.00.'+fdate+'.000000.png'
    if np.unique(el)[0] == 0 and np.unique(az)[0] == 0:
        outfile = '/home/theisen/www/minimpl/data/fpt/sgpminimplS01.00.'+fdate[0:8]+'.000000.nc'
        mpl = mpl.drop('time_utc')
        mpl.to_netcdf(outfile)

        display = act.plotting.TimeSeriesDisplay(mpl, subplot_shape=(2,), figsize=(10,8))
        plt.subplots_adjust(left=0.1, bottom=0.075,top=0.95, hspace=0.15)
        title = 'NRB CoPol at ' + fdate
        display.plot('nrb_copol', cmap='jet', vmin=0, vmax=1, subplot_index=(0,), set_title=title)
        title = 'Depolarization Ratio at ' + fdate
        display.plot('depol', cmap='jet', vmin=0, vmax=100, subplot_index=(1,), set_title=title)
        print('Saving to '+filename)
        plt.savefig('/home/theisen/www/minimpl/images/fpt/'+filename)
        #plt.savefig('/home/theisen/www/minimpl/images/test/'+filename)
        plt.close()
    mpl.close()
    #radar = act.utils.create_pyart_obj(mpl, azimuth='azimuth_angle', elevation='elevation_angle',
    #                                   range_var='range')


#display = pyart.graph.RadarDisplay(radar)
#display.plot('nrb_copol', sweep=1, title_flag=False, vmin=0, vmax=1.0,cmap='jet')
#plt.show()

