import glob
import act
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import pandas as pd
import xarray as xr

# Create a function to determine if a day is a weekday
def is_weekday(date):
    if date.isoweekday() in (6, 7):
        return "weekday"
    else:
        return "weekday"

files = glob.glob('/home/theisen/test/crg*tsv')
files.sort()
skip = np.arange(0,34)
skip = np.append(skip, [35, 36, 37, 38])
ds = act.io.read_csv(files, skiprows=skip, header=0, sep='\t')

time = [np.datetime64(ds['Date'].values[i]+'T'+ds['Time'].values[i]) for i in range(len(ds['Date'].values))]

ds['Time'].values = time
ds = ds.drop_vars('Time')
ds = ds.assign_coords({'index': time})
ds = ds.rename({'index': 'time'})

time_pd = pd.to_datetime(ds['time'].values)
is_weekday = time_pd.weekday >= 5

ds =ds.where(is_weekday == False)

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

variable = 'sum_counts'
result = ds.qcfilter.add_delta_test(variable, diff_limit=30)
#ds.qcfilter.datafilter(variable, rm_assessments=['Bad', 'Suspect'], del_qc_var=False)


display = act.plotting.TimeSeriesDisplay(ds, figsize=(10,9), subplot_shape=(3,))
title = 'CRG Monitoring OPC Temperature and RH'
display.plot('Temp_i', subplot_index=(0,), set_title=title)
display.axes[0].set_ylabel('Temperature (ºC)')
ax2 = display.axes[0].twinx()
ax2.plot(ds['time'], ds['rH_i'], color='orange')
ax2.set_ylabel('Relative Humidity (%)')

title = 'CRG Monitoring OPC Counts'
display.plot('counts', subplot_index=(1,), norm=colors.LogNorm(vmin=1., vmax=1000.), set_title=title)
title = 'CRG Monitoring OPC Sum of Counts'
display.plot('sum_counts', subplot_index=(2,), set_title=title)
#display.axes[1].pcolormesh(time, diameter_midpoint, data, shading='nearest', norm=colors.LogNorm())
#display.axes[1].set_ylabel('Diameter Midpoint')
filename = 'crgaosopcmonS2.00.weekday.000000.png'
plt.savefig('/data/www/userplots/theisen/crgaosopcmon/' + filename)

#----------Wind Rose Plots----------#
files = glob.glob('/data/datastream/crg/crgmetwxtS2.b1/*.202504*.nc')
ds_met = act.io.read_arm_netcdf(files)
ds_merge = xr.merge([ds_met.resample(time='1min').nearest(), ds.resample(time='1min').nearest()])

display = act.plotting.WindRoseDisplay(ds_merge)
display.plot_data('wdir_vec_mean', 'wspd_vec_mean', 'sum_counts', num_dirs=15, plot_type='line', line_plot_calc='mean')
filename = 'crgaosopcmonS2.00.weekday_rose.000000.png'
plt.savefig('/data/www/userplots/theisen/crgaosopcmon/' + filename)


display = act.plotting.WindRoseDisplay(ds_merge)
display.plot_data('wdir_vec_mean', 'wspd_vec_mean', 'sum_counts', num_dirs=15, plot_type='contour', contour_type='mean')
filename = 'crgaosopcmonS2.00.weekday_rose_contour.000000.png'
plt.savefig('/data/www/userplots/theisen/crgaosopcmon/' + filename)

display = act.plotting.WindRoseDisplay(ds_met)
display.plot('wdir_vec_mean', 'wspd_vec_mean', spd_bins=[0,5,10,15])
filename = 'crgaosopcmonS2.00.all_wind_rose.000000.png'
plt.savefig('/data/www/userplots/theisen/crgaosopcmon/' + filename)
