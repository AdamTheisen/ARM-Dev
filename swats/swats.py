import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates

files = glob.glob('/home/theisen/Code/swats/data/*nc')
#files.extend(glob.glob('/data/archive/sgp/sgpswatsE13.b1/*.201*nc'))

obj = act.io.armfiles.read_netcdf(files)


#variable = 'watcont_W'
#if variable not in obj:
variable = 'watcont_w'
depth = ['5 cm', '15 cm', '25 cm', '35 cm', '60 cm', '85 cm']

obj[variable].attrs['units'] = 'm3/m3'

myFmt = mdates.DateFormatter('%m-%Y')

display = act.plotting.TimeSeriesDisplay(obj, figsize=(15,10))
display.plot(variable, force_line_plot=True)
display.axes[0].legend(depth)
display.axes[0].xaxis.set_major_formatter(myFmt)
plt.savefig('/home/theisen/www/swats.png')

