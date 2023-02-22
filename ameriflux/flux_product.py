import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import xarray as xr


facs = ['E31']
datastreams = ['ecorsf', 'sebs', 'amc']

date = '20210501'
for f in facs:
    ecor = None
    sebs = None
    amc = None
    obj = []

    ecor_files = glob.glob('/data/archive/sgp/sgpecorsf' + f + '.b1/*' + date + '*')
    if len(ecor_files) > 0:
        ecor =  act.io.armfiles.read_netcdf(ecor_files)
        obj.append(ecor)

    amc_files = glob.glob('/data/archive/sgp/sgpamc' + f + '.b1/*' + date + '*')
    if len(amc_files) > 0:
        amc =  act.io.armfiles.read_netcdf(amc_files)
        obj.append(amc)

    sebs_files = glob.glob('/data/archive/sgp/sgpamc' + f + '.b1/*' + date + '*')
    if len(sebs_files) > 0:
        sebs =  act.io.armfiles.read_netcdf(sebs_files)
        obj.append(sebs)

    print(ecor)
    obj = xr.merge(obj)

    print(obj)

    ecor.close()
    sebs.close()
    amc.close()

#display = act.plotting.TimeSeriesDisplay(obj, figsize=(15,10))
#display.plot('o3')
#plt.savefig('/home/theisen/www/mos_o3.png')

