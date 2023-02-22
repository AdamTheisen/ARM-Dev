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
import datetime as dt
import os


files = glob.glob('/data/datastream/sgp/sgpmplS01.00/*')
files.sort()

t1 = dt.datetime.now() - dt.timedelta(minutes=122)
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

prev_date = ''
for d in dates:
    fdate = d.strftime('%Y%m%d')
    dfile = glob.glob('/data/datastream/sgp/sgpmplS01.00/*raw.'+fdate+'*')

    obj = []
    for f in dfile:
        mini = act.io.mpl.read_sigma_mplv5(f, afterpulse=ap, dead_time=dt, overlap=op)
        #data = 10. * np.log10(mini['nrb_copol'].values)
        #mini['nrb_copol'].values = data
        #mini['nrb_copol'].attrs['units'] = '10 * log10(' +  mini['nrb_copol'].attrs['units'] + ')'
        obj.append(mini)
    mini = xr.merge(obj)

    mpl_file = glob.glob('/data/datastream/sgp/sgpmplpolfsC1.b1/*'+fdate+'*.nc')
    mpl = act.io.armfiles.read_netcdf(mpl_file)
    mpl = act.corrections.mpl.correct_mpl(mpl)

    az = mini['azimuth_angle'].values
    el = mini['elevation_angle'].values
    filename = 'sgpminimplS01.00.'+fdate+'.png'
    if np.unique(el)[0] == 0 and np.unique(az)[0] == 0:
        display = act.plotting.TimeSeriesDisplay({'MiniMPL': mini, 'MPLPOLFS': mpl}, subplot_shape=(2,), figsize=(10,8))
        plt.subplots_adjust(left=0.1, bottom=0.075,top=0.95, hspace=0.15)
        title = 'NRB CoPol at ' + fdate
        display.plot('nrb_copol', dsname='MiniMPL', cmap='jet', vmin=0, vmax=1, subplot_index=(0,), set_title=title)
        title = 'SGP MPLPOLFS on ' + fdate[0:8]
        display.plot('signal_return_co_pol', dsname='MPLPOLFS', cmap='jet', vmin=0, vmax=20, subplot_index=(1,), set_title=title)
        display.set_xrng([mini['time'].values[0], mini['time'].values[-1]])
        plt.savefig('/home/theisen/www/minimpl/images/mpl_comp/'+filename)
        #plt.savefig('/home/theisen/www/minimpl/images/test/'+filename)
        plt.close()
    mini.close()
    #radar = act.utils.create_pyart_obj(mpl, azimuth='azimuth_angle', elevation='elevation_angle',
    #                                   range_var='range')


#display = pyart.graph.RadarDisplay(radar)
#display.plot('nrb_copol', sweep=1, title_flag=False, vmin=0, vmax=1.0,cmap='jet')
#plt.show()

