import act
import glob


sites = ['fkb']
inst = '1290rwpwindmom'
fac = ['M1']
lev = 'a0'

data_dir = '/data/archive/'

for i, s in enumerate(sites):
    ds = s + inst + fac[i] + '.' + lev
    print(data_dir + s + '/' + ds)
    files = glob.glob(data_dir + s + '/' + ds + '/*.200706*')
    files.sort()
    print(s, len(files))
    ct = 0
    for f in files:
        obj = act.io.arm.read_arm_netcdf(f)
        if obj['snr'].max() == 32767:
            print(f)
            ct += 1
    print('Total files in error: ', ct)
