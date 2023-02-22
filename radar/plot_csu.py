import act
import pyart
import glob
import cartopy.crs as ccrs
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime as dt
import subprocess


today = dt.date.today().strftime("%Y%m%d")
yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime("%Y%m%d")
now = dt.datetime.now()
ago = now-dt.timedelta(minutes=20)
fdate = today

files = glob.glob('/data/datastream/guc/gucxprecipradarS2.00/*csu.sail-' + today + '*')
yfiles = glob.glob('/data/datastream/guc/gucxprecipradarS2.00/*csu.sail-' + yesterday + '*_PPI.nc')
files += yfiles
files.sort()

for f in files:
    stat = os.stat(f)
    mtime = dt.datetime.fromtimestamp(stat.st_mtime)
    if mtime < ago:
        continue
    print("Processing: " + f)
    f_comp = f.split('_')[0].split('-')
    fdate = str(f_comp[-2])
    ftime = (f_comp[-1])
    f_comp = f.split('.')[-2].split('_')
    scan_info = '_'.join([f_comp[-1], f_comp[-2]]) 
    #obj = xr.open_dataset(f)
    #time = obj['Time'].values
    #obj = obj.rename({'Time': 'time', 'Azimuth': 'azimuth', 'Elevation': 'elevation'})
    #obj['latitude'] = obj.attrs['Latitude']
    #obj['longitude'] = obj.attrs['Longitude']
    #obj['altitude'] = obj.attrs['Height']
    #values = obj['StartRange'].values[0] / -1000. + obj['GateWidth'].values[0]/1000. * range(0,obj.attrs['NumGates'])
    #if np.nanmax(values) < 5.:
    #    continue
    #
    #atts = {'units': 'm', 'long_name': 'Distance to bin'}
    #da = xr.DataArray(values, attrs=atts)
    #obj['range'] = da
    #obj = obj.rename({'Radial': 'time', 'Gate': 'range'})
    #obj['range'].values = values
    #obj['time'].values = time
    #
    #radar = act.utils.create_pyart_obj(obj, range_var='range')

    radar = pyart.io.read(f)
    display = pyart.graph.RadarDisplay(radar)

    title = 'SAIL X-Band Radar at Crested Butte, CO\n' + str(fdate) + ' ' + str(ftime) + \
            '    El:' + str(np.round(np.nanmean(radar.elevation['data']), decimals=1))
    fig = plt.figure(figsize=(7.5,6))
    if radar.scan_type == 'other':
        display.plot_ppi('DBZ', 0, vmin=-20, vmax=40,
                     mask_tuple=['NCP', 0.5],
                     title=title, fig=fig)
    else:
        display.plot('DBZ', 0, vmin=-20, vmax=40,
                     mask_tuple=['NCP', 0.5],
                     title=title, fig=fig)
    display.set_limits(xlim=(-40, 40), ylim=(-40, 40))

  
    directory = '/home/theisen/www/sail_radar/images/'+str(fdate)
    if not os.path.exists(directory):
        os.makedirs(directory) 
    plt.savefig(directory + '/gucxprecipradarS2.00.' + str(fdate) + '.' + str(ftime) + '.' + scan_info + '.png')
    plt.close(fig=fig)

el = ['1', '2', '4']
for e in el:
    cmd = 'convert -loop 0 /home/theisen/www/sail_radar/images/'+str(fdate)+'/*PPI_'+e+'.png '
    cmd = cmd + '/home/theisen/www/sail_radar/movies/' + str(fdate) + '/'+'PPI_'+e+'.gif'
    if not os.path.exists('/home/theisen/www/sail_radar/movies/' + str(fdate)):
        os.makedirs('/home/theisen/www/sail_radar/movies/' + str(fdate))
    os.system(cmd)
