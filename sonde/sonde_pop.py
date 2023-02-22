import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates
import xarray as xr
import numpy as np

guc_lat = 38.95616
guc_lon = -106.9879

files = glob.glob('/data/archive/guc/gucsondewnpnM1.b1/*cdf')
files.sort()
sonde = []
sample = None
for f in files[11:]:
    obj = act.io.armfiles.read_netcdf(f)
    obj = obj.where(obj['time'] == obj['time'].values[-1], drop=True)
    if sample is None:
        sample = obj
    sonde.append(obj)

sample['lat'].values = [guc_lat]
sample['lon'].values = [guc_lon]
sonde.append(sample)

obj = xr.merge(sonde)

display = act.plotting.GeographicPlotDisplay(obj, figsize=(15,10))
ax = display.geoplot('lat')
ax.plot(guc_lon, guc_lat, 'k*', markersize=14)

plt.savefig('/home/theisen/www/guc_sonde_location.png')
