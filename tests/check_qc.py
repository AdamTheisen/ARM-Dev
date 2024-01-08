import act
import glob

files = glob.glob('/data/archive/sgp/sgpmetE13.b1/*.201*')
files.sort()
for f in files:
    ds = act.io.read_arm_netcdf(f)
    if ds['qc_temp_mean'].max() > 0:
        print(f, float(ds['qc_temp_mean'].max()))
