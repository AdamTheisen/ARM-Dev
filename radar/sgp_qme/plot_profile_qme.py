import act
import glob
import sys
import numpy as np
import matplotlib.pyplot as plt

files = glob.glob('/data/dq/qme/sgp/sgpxsaprrawI4.00/*')
files.sort()

time = []
profile_zh = []
fig, ax = plt.subplots()
for f in files:
    try:
        obj = act.io.armfiles.read_netcdf(f, decode_times=False, drop_variables=['rain_time'], cftime_to_datetime64=False)
        date = str(np.unique(obj['date'].values)[0])
        obj = obj.where(obj['time'] > 0., drop=True)
        dummy_t = obj['time'].values.astype('int')
        dummy = [np.datetime64('-'.join([date[0:4], date[4:6], date[6:8]]) + 'T' + ':'.join([str(t).zfill(6)[0:2], str(t).zfill(6)[2:4], str(t).zfill(6)[4:6]])) for t in dummy_t]
        plt.pcolormesh(dummy, obj['height'], np.transpose(obj['profile_zh'].values), edgecolors='none', vmin=0, vmax=50)
        obj.close()
        #time = np.append(time, dummy)
        #profile_zh = np.append(profile_zh, obj['profile_zh'].values)
    except:
        print(f)
        continue

plt.colorbar()
#fig, ax = plt.subplots()
#ax.plot(time, profile_zh)
fig.savefig('/home/theisen/www/sgpxsaprI4_profile.png')
