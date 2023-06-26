import act
import glob


sites = ['sgp']
inst = 'irt'
fac = ['E13']
lev = 'b1'

data_dir = '/data/archive/'

for i, s in enumerate(sites):
    ds = s + inst + fac[i] + '.' + lev
    print(data_dir + s + '/' + ds)
    files11 = glob.glob(data_dir + s + '/' + ds + '/*.20080620*')
    files12 = glob.glob(data_dir + s + '/' + ds + '/*.2009*')
    files = files11 + files12
    files.sort()
    print(s, len(files))
    ct = 0
    for f in files:
        obj = act.io.armfiles.read_netcdf(f)
        try:
            cal = obj.attrs['calibration_factor']
        except:
            cal = obj.attrs['calib_coeff']
        if cal != '1.410000':
            print(f)
            ct += 1
    print('Total files in error: ', ct)
