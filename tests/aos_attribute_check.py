import act
import glob


sites = ['sgp', 'nsa', 'pgh']
inst = 'aoscpc'
fac = ['C1', 'X1', 'M1']
lev = 'a1'

data_dir = '/data/archive/'

for i, s in enumerate(sites):
    ds = s + inst + fac[i] + '.' + lev
    print(data_dir + s + '/' + ds)
    files11 = glob.glob(data_dir + s + '/' + ds + '/*.2011*')
    files12 = glob.glob(data_dir + s + '/' + ds + '/*.2012*')
    files = files11 + files12
    print(s, len(files))
    ct = 0
    for f in files:
        obj = act.io.armfiles.read_netcdf(f)
        for a in obj.attrs:
            if '3372' in str(obj.attrs[a]) or '3772' in str(obj.attrs[a]):
                if s == 'sgp':
                    print(f, obj.attrs[a])
                ct += 1
    print('Total files in error: ', ct)
