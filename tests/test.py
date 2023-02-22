import matplotlib
matplotlib.use('Agg')

import act
import glob
import matplotlib.pyplot as plt
import json
import numpy as np

site = 'nsa'
fac = 'C1'
if site in ['oli']:
    fac = 'M1'
files = glob.glob('/data/dq/qme/'+site+'/'+site+'kazrge'+fac+'.a1/*')


time = []
noise = []
var = 'noise'
var = 'diff_kazrmd_zh'
for f in files:
    # Read in KAZR data to Standard Object
    try:
        obj = act.io.armfiles.read_netcdf(f)
        obj = obj.resample(time='1D').mean()
        noise += list(obj[var].values)
        time += list(obj['time'].values)
    except:
        continue

fig, ax = plt.subplots(figsize=(15,10))
ax.plot(time, noise, '.')
plt.title(site + ' KAZR Noise Floor Daily Means')

# Save figure
plt.savefig('./images/'+site+'_kazr_'+var+'.png')
plt.clf()
obj.close()

