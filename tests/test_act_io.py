import glob
import xarray as xr
import act

import warnings
warnings.filterwarnings("ignore")


site = 'sgp'
dirs = glob.glob('/data/archive/' + site + '/*C1.*')
dirs.sort()

dirs = dirs[620:]
ct = 0
for d in dirs:
    #print(ct)
    ct += 1
    files = glob.glob(d + '/*')
    if len(files) <= 1:
        continue
    test_files = files[-3:-1]

    if test_files[0].endswith('tar') or test_files[0].endswith('png') or test_files[0].endswith('mpg') or test_files[0].endswith('mp4'):
        continue

    try:
        ds = xr.open_dataset(test_files[0])
    except:
        print('Single File Fail: ', d)
        continue

    try:
        ds = xr.open_mfdataset(test_files)
    except:
        print('Multi-File Fail: ', d)
        continue

    try:
        ds = act.io.read_arm_netcdf(test_files[0])
    except:
        print('Single File ACT Fail: ', d)

    try:
        ds = act.io.read_arm_netcdf(test_files)
    except:
        print('Multiple File ACT Fail: ', d)
