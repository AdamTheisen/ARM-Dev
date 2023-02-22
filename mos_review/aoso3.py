import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import xarray as xr

files = glob.glob('/data/datastream/mos/mosaoso3M1.b1/*20*')
#obj = act.io.armfiles.read_netcdf(files)
obj = xr.open_mfdataset(files)

display = act.plotting.TimeSeriesDisplay(obj, figsize=(15,10))
display.plot('o3')
plt.savefig('/home/theisen/www/mos_o3.png')

obj.close()
