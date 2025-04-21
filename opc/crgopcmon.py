import glob
import act
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import pandas as pd
import xarray as xr

today = dt.today().strftime('%Y%m%d')
yesterday = (dt.now() - timedelta(days=1)).strftime('%Y%m%d')

files = glob.glob('/data/datastream/crg/crgaosopcmonS2.00/*' + today + '*')
files.sort()
skip = np.arange(0,34)
skip = np.append(skip, [35, 36, 37, 38])
ds = act.io.read_csv(files, skiprows=skip, header=0, sep='\t')

time = [np.datetime64(ds['Date'].values[i]+'T'+ds['Time'].values[i]) for i in range(len(ds['Date'].values))]
ds['Time'].values = time
ds = ds.drop_vars('Time')
ds = ds.assign_coords({'index': time})
ds = ds.rename({'index': 'time'})

bin_vars = [b for b in list(ds) if 'Bin' in b]

diameter_midpoint = np.array([0.2745797, 0.3238765, 0.3817434, 0.4494797, 0.5301773, 
    0.6253831, 0.737021, 0.868562, 1.02402, 1.206946, 1.422656, 1.677333, 
    1.976832, 2.330103, 2.746718, 3.23755, 3.23755, 3.816564, 4.49881, 
    5.302564, 6.250821, 7.368582, 8.68562, 10.2402, 12.06947, 14.22656, 
    16.77333, 19.76832, 23.30103, 27.46718, 32.3755, 35])

data = []
for ii, v in enumerate(bin_vars):
    if len(data) == 0:
        data = ds[v].values
    else:
        data = np.vstack([data, ds[v].values])

long_name = 'Raw Data Counts'
attrs = {'long_name': long_name, 'units': 'counts'}
da = xr.DataArray(np.transpose(data), dims=['time', 'diameter_midpoint'], coords={'time': ds['time'].values, 'diameter_midpoint': diameter_midpoint}, attrs=attrs)
ds['counts'] = da
long_name = 'Sum of Data Counts'
attrs = {'long_name': long_name, 'units': 'counts'}
da = xr.DataArray(np.nansum(data, axis=0), dims=['time'], coords={'time': ds['time'].values}, attrs=attrs)
ds['sum_counts'] = da
#for ii, v in enumerate(bin_vars):
#    if len(data) == 0:
#        data = ds[v].values
#    elif ('16' in v):
#        avg = np.mean(np.vstack([ds['Bin 16'].values, ds['Bin 17'].values]), axis=0)
#        avg = avg - ds[bin_vars[ii + 2]]
#        data = np.vstack([data, avg])
#    elif ('17' in v):
#        continue
#    elif ii == len(bin_vars)-1:
#        data = np.vstack([data, np.zeros(len(ds['time'].values))])
#    else:
#        data = np.vstack([data, ds[v].values - ds[bin_vars[ii+1]]])

# Compute dlogDp and geometric bin centers
#max_column = 32
#dp_bin = [dp(1:max_column-2), dp(2:max_column-1)]
#dp_geo = geomean(dp_bin, 2)
#dlogdp = log10(dp_bin(:,2) ./ dp_bin(:,1))
#dn = data / 100.

display = act.plotting.TimeSeriesDisplay(ds, figsize=(10,9), subplot_shape=(3,))
display.plot('Temp_i', subplot_index=(0,))
display.axes[0].set_ylabel('Temperature (ºC)')
ax2 = display.axes[0].twinx()
ax2.plot(ds['time'], ds['rH_i'], color='orange')
ax2.set_ylabel('Relative Humidity (%)')

display.plot('counts', subplot_index=(1,), norm=colors.LogNorm(vmin=1., vmax=1000.))
display.plot('sum_counts', subplot_index=(2,))
#display.axes[1].pcolormesh(time, diameter_midpoint, data, shading='nearest', norm=colors.LogNorm())
#display.axes[1].set_ylabel('Diameter Midpoint')
filename = 'crgaosopcmonS2.00.daily_status.' + today + '.000000.png'
plt.savefig('/data/www/userplots/theisen/crgaosopcmon/' + filename)
