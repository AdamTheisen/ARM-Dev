import radtraq
import glob
import act
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr


files = glob.glob('/data/datastream/hou/houcsapr2cfrS2.a1/houcsapr2cfrS2.a1.20220506.0*.nc')

prof=[]
for f in files:
    obj = act.io.armfiles.read_netcdf(f)

    if obj.attrs['scan_name'] == 'hsrhi':
        obj = obj.where(obj['azimuth'] <= 56, drop=True)
        profile_obj = radtraq.proc.profile.extract_profile_at_lat_lon(obj,  30.1, -95.883339)
        if len(profile_obj['reflectivity'].values[0]) == 3:
            prof.append(profile_obj['reflectivity'])
    obj.close()

obj = xr.merge(prof)

fig, ax = plt.subplots()
#ax.pcolormesh(profile_obj['time'], profile_obj['height'], np.transpose(profile_obj['reflectivity'].values))
ax.pcolormesh(np.transpose(obj['reflectivity'].values), vmin=-20, vmax=50, cmap='jet')

#display = act.plotting.TimeSeriesDisplay(profile_obj)
#display.plot('reflectivity')
plt.title('Extracted Reflectivity from 30.1, -95.88')
plt.savefig('/home/theisen/www/csapr2_profile.png')

obj.close()
