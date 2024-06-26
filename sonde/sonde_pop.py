import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates
import xarray as xr
import numpy as np

#guc_lat = 38.95616
#guc_lon = -106.9879
site = 'sgp'
lat = 36.605
lon = -97.485
#site = 'nsa'
#lat = 71.323
#lon = -156.609

files = glob.glob('/data/archive/'+site+'/'+site+'sondewnpnC1.b1/*cdf')
files = glob.glob('/Users/atheisen/Code/development-space/data/sgpsondewnpnC1.b1/*')
files.sort()
sonde = []
sample = None
ds = None
print(files)
for f in files:
        obj = act.io.arm.read_arm_netcdf(f)
        obj = obj.where(obj['time'] == obj['time'].values[-1], drop=True)
        if obj['lat'].values[0] == -9999 or obj['lon'].values[0] == -9999:
            continue
        #if obj['lat'].values[0] > 40. or obj['lat'].values[0] < 30. or obj['lon'].values[0] > -80. or obj['lon'].values[0] < -100:
#        if obj['lat'].values[0] > 80. or obj['lat'].values[0] < 60. or obj['lon'].values[0] > -140. or obj['lon'].values[0] < -180:
            print(f)
            continue
        obj['lat'].values = [-40.6808]
        obj['lon'].values = [144.69]
        if sample is None:
            sample = obj
        if ds is None:
            ds = obj
        else:
            ds = xr.merge([ds, obj])
#sample['lat'].values = [lat]
#sample['lon'].values = [lon]
#ds = xr.merge([ds, sample])

print(ds)

display = act.plotting.GeographicPlotDisplay(ds, figsize=(15,10))
ax = display.geoplot('time')
ax.plot(lon, lat, 'k*', markersize=14)
print(ds['lat'].min())
print(ds['lon'].min())
plt.savefig('./images/'+site+'_sonde_location.png')
