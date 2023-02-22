import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates

files = glob.glob('/data/datastream/hou/houkazrcfrgeauxM1.a0/*20210921*')

obj = act.io.armfiles.read_netcdf(files)
obj = obj.resample(time='1min').nearest()

display = act.plotting.TimeSeriesDisplay(obj, figsize=(15,10), subplot_shape=(2,))
display.plot('roll', subplot_index=(0,))
display.plot('pitch', subplot_index=(1,))
plt.savefig('/home/theisen/www/hou_kazr_rph.png')
