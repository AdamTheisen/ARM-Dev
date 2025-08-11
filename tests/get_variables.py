import act
import glob

sites = ['sgp', 'nsa', 'ena', 'crg', 'kcg', 'bnf']
ds_name = 'met'
date='20250801'

for s in sites:
    ds = glob.glob('/data/datastream/' + s + '/' + s + ds_name + '*.b1')

    for d in ds:
        if 'wxt' in d:
            continue
        files = glob.glob(d + '/*' + ds_name + '*.' + date + '*')
        if len(files) == 0:
            continue
        ds = act.io.read_arm_netcdf(files)
        [print(v) for v in ds.keys()]
