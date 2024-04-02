import act
import glob

files = glob.glob('/data/archive/sgp/sgppgsC1.b1/*.2023*')
ds = act.io.read_arm_netcdf(files)

print(ds)
