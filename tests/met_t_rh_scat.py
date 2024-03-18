import act
import glob

sites = ['sgp']
inst = 'met'
fac = ['E13']
lev = 'b1'

data_dir = '/data/archive/'

for i, s in enumerate(sites):
    ds = s + inst + fac[i] + '.' + lev
    print(data_dir + s + '/' + ds)
    files = glob.glob(data_dir + s + '/' + ds + '/*.2023*')
    files.sort()
    ds = act.io.armfiles.read_netcdf(files)
    ds = ds.where(ds['temp_mean'].compute() > 25., drop=True)
