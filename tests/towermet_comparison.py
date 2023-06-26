import act
import glob
import matplotlib.pyplot as plt


sites = ['sgp']
inst = '1440twr25mC1.a0'
fac = ['C1']
lev = 'a0'

data_dir = '/data/archive/'

for i, s in enumerate(sites):
    files25 = glob.glob(data_dir + s + '/' + 'sgp1twr25mC1.a0' + '/*.970529*')
    files25.sort()
    files60 = glob.glob(data_dir + s + '/' + 'sgp1twr60mC1.a0' + '/*.970529*')
    files60.sort()


    ds25 = act.io.armfiles.read_netcdf(files25, compat='override')
    ds60 = act.io.armfiles.read_netcdf(files60, compat='override')

    display = act.plotting.TimeSeriesDisplay({'25m': ds25, '60m': ds60})
    display.plot('rh', dsname='25m', label='25m')
    display.plot('rh', dsname='60m', label='60m')
    plt.legend()
    plt.savefig('/data/www/userplots/theisen/reproc/sgptwrmet_comp.png')
