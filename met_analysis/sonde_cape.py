import act
import glob
import numpy as np
import matplotlib.pyplot as plt


files = glob.glob('/data/archive/mao/maosondewnpnM1.b1/*')
files.sort()

cape = []
time = []

for f in files:
    try:
        obj = act.io.armfiles.read_netcdf(f)
        obj = act.retrievals.calculate_stability_indicies(obj, temp_name='tdry', td_name='dp', p_name='pres', rh_name='rh')
        cape.append(obj['surface_based_cape'].values)
        time.append(obj['time'].values[0])
    except:
        continue
fig, ax = plt.subplots()
ax.plot(time, cape, '.')
fig.savefig('/home/theisen/www/mao_sonde_cap.png')
