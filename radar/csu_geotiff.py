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
import warnings


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
    if mtime < ago:
        continue

    print("Processing: " + f)
    f_comp = f.split('_')[0].split('-')
    fdate = str(f_comp[-2])
    ftime = (f_comp[-1])
    f_comp = f.split('.')[-2].split('_')
    scan_info = '_'.join([f_comp[-1], f_comp[-2]]) 
    radar = pyart.io.read(f)
    if '_2_PPI' in files[i + 1]:
        radar2 = pyart.io.read(files[i + 1])
        radar = pyart.util.join_radar(radar, radar2)

    grid = pyart.map.grid_from_radars((radar,),
        grid_shape=(1, 444, 444),
        grid_limits=((500, 500), (-40000.0, 40000.0), (-40000.0, 40000.0)),
        fields=['DBZ'])
    
    directory = '/home/theisen/www/sail_radar/tiff/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    tiff_file = directory + '/' + 'gucxprecipradarS2.00.' + fdate + '.'+ ftime +'.tif'
    
    pyart.io.write_grid_geotiff(grid, tiff_file, 'DBZ', rgb=True, cmap='pyart_HomeyerRainbow', vmin=-20, vmax=40, level=0)
