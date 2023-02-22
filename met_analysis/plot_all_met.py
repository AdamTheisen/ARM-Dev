import act
import matplotlib.pyplot as plt
import glob

files = glob.glob('/data/archive/sgp/sgpmetE13.b1/*.2022*cdf')

obj = act.io.armfiles.read_netcdf(files)

display = act.plotting.TimeSeriesDisplay(obj, figsize=(16,6))
display.plot('temp_mean')
plt.tight_layout()
plt.savefig('./sgpE13_met_2022.png')
