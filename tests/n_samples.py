import act
import glob
from scipy.stats import mode
import matplotlib.pyplot as plt

#files = glob.glob('/data/archive/bnf/bnfaosccn2colaavgM1.b1/*.2025*')
files = glob.glob('/data/archive/bnf/bnfaosccn200M1.a1/*.2025*')
files.sort()
data = []
time = []
for f in files:
    ds = act.io.read_arm_netcdf(f)

    data.append(len(ds['time'].values))
    time.append(ds['time'].values[0])


fig, ax = plt.subplots(figsize=(15,10))
ax.plot(time, data)

# Save figure
plt.savefig('/data/www/userplots/theisen/n_samples.png')
plt.clf()


