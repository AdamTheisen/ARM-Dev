import act
import glob
from scipy.stats import mode

files = glob.glob('/data/archive/bnf/bnfhsrlM1.a1/*.202509*')
files.sort()
data = []
for f in files:
    ds = act.io.read_arm_netcdf(f)

    print(len(ds['time'].values))
    data.append(len(ds['time'].values))

print(mode(data))
