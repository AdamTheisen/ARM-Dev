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
    files = glob.glob(data_dir + s + '/' + ds + '/*.1994*')
    files.sort()
    print(s, len(files))
    ct = 0
    for f in files:
        obj = act.io.armfiles.read_netcdf(f)
        if obj['temp_mean'].min() <= -5.:
            print(f)
            ct += 1
    print('Total files in error: ', ct)
