import act
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

ds = 'corsondewnpnM1.b1'
ds2 = 'cormetM1.b1'
site = 'cor'

sonde_files = glob.glob('/data/archive/cor/' + ds + '/*cdf')
sonde_files = sorted(sonde_files)
sonde_files = sonde_files[2:]

prev_date = '20000101'
time = []
sonde = []
met = []
diff = []
for f in sonde_files:
    sonde_obj = act.io.armfiles.read_netcdf(f)
    date = f.split('.')[-3]
    if date != prev_date:
        met_files = glob.glob('/data/archive/cor/' + ds2 + '/*'+date+'*cdf')
        if len(met_files) == 0:
            continue
        met_obj = act.io.armfiles.read_netcdf(met_files)
        prev_date = date

    try:
        test = met_obj['temp_mean'].sel(time=sonde_obj['time'].values[0])
    except:
        continue
    time.append(sonde_obj['time'].values[0])
    sonde.append(sonde_obj['tdry'].values[0] + 1.5)
    met.append(test.values)
    diff.append(test.values - sonde_obj['tdry'].values[0] - 1.5)

sonde_da = xr.DataArray(data=sonde, dims=['time'], coords=dict(time=time))
met_da = xr.DataArray(data=met, dims=['time'], coords=dict(time=time))
diff_da = xr.DataArray(data=diff, dims=['time'], coords=dict(time=time))
obj = xr.Dataset(data_vars={'sonde_temp': sonde_da, 'met_temp': met_da, 'difference': diff_da})

test = obj.where(obj['difference']>1, drop=True)
print(test['time'].values)

display = act.plotting.TimeSeriesDisplay({'CACTI_SONDE_MET': obj}, subplot_shape=(2,), figsize=(10,8))
display.plot('met_temp', ls='-', subplot_index=(0,))
display.plot('sonde_temp', ls='-', subplot_index=(0,))
display.plot('difference', ls='-', subplot_index=(1,))
display.axes[1].text(obj['time'].values[0], 10, 'avg: ' + str(np.round(np.nanmean(diff),2)))
display.axes[1].text(obj['time'].values[0], 8, 'med: ' + str(np.round(np.nanmedian(diff),2)))
display.axes[1].set_ylim([0,12])
plt.tight_layout()
plt.savefig('/home/theisen/www/cor_sonde_met_1_5.png')

