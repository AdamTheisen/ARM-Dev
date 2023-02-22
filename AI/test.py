import act
import glob
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


files = glob.glob('/data/archive/sgp/sgpmetE13.b1/*')
obj = act.io.armfiles.read_netcdf(files, parallel=True)

date_form = DateFormatter("%m-%d-%Y")

display = act.plotting.TimeSeriesDisplay(obj, figsize=(16,7))
display.plot('temp_mean', marker='')
display.set_yrng([-40, 60])
display.axes[0].xaxis.set_major_formatter(date_form)
plt.savefig('/home/theisen/www/sgpmet.png')
plt.tight_layout()
obj.close()
