import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates

files = glob.glob('/data/archive/sgp/sgpaosmetE13.a1/*.2020*nc')
files = glob.glob('/data/datastream/hou/houaosmetM1.a1/*20200913*nc')

obj = act.io.armfiles.read_netcdf(files)

display = act.plotting.HistogramDisplay(obj, figsize=(15,10))
#display.plot_stacked_bar_graph('wspd_vec_mean')
display.plot_stacked_bar_graph('wind_speed')
plt.savefig('/home/theisen/www/hou_aosmet_wind_20210913.png')
