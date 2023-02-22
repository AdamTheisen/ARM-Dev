import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import xarray as xr

for i in range(9):

    date='201'+str(i+1)
    print(date)
    files = glob.glob('/data/archive/sgp/sgpmwr3cC1.b1/*.'+date+'*')
    obj = act.io.armfiles.read_netcdf(files)

    display = act.plotting.TimeSeriesDisplay(obj, figsize=(15,10))
    display.plot('pwv')
    plt.savefig('/home/theisen/www/pwv_'+date+'.png')

    obj.close()
