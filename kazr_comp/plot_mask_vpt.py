"""
Example on how to calculate and plot average profiles
-----------------------------------------------------

This example shows how to calculate and plot average profiles
from masked data

"""


import radtraq
import act
import matplotlib.pyplot as plt
import numpy as np
import glob

# Read in Example KAZR File using ACT
f = glob.glob('/data/datastream/hou/houkazrcfrgeM1.a1/*20210806*')
f.sort()
ge = act.io.armfiles.read_netcdf(f)

f = glob.glob('/data/datastream/hou/houkazrcfrmdM1.a1/*20210806*')
f.sort()
md = act.io.armfiles.read_netcdf(f)

# Resample to 1-minute to simplify processing
ge = ge.resample(time='1min').nearest()
md = md.resample(time='1min').nearest()

# Process cloud mask in order to properly produce average VPT profiles through cloud
ge = radtraq.proc.cloud_mask.calc_cloud_mask(ge, 'reflectivity', 'range')
md = radtraq.proc.cloud_mask.calc_cloud_mask(md, 'reflectivity', 'range')

# Variables to calculate average profiles
variable = ['reflectivity', 'mean_doppler_velocity']

# Create a grid to interpolate data onto - Needed for different radars
fh = 1500.
ygrid = np.arange(fh, 15000, 50)

# Calculate average profiles
ge = radtraq.proc.profile.calc_avg_profile(ge, variable=variable, first_height=fh, ygrid=ygrid)
md = radtraq.proc.profile.calc_avg_profile(md, variable=variable, first_height=fh, ygrid=ygrid)

#ge = ge.where(ge['mask2'] == 1)
#md = md.where(md['mask2'] == 1)

# Plot data using ACT
#display = act.plotting.TimeSeriesDisplay(ge)
#display.plot('reflectivity', cmap='jet')
#display.axes[0].set_ylim([0, 20000])
#plt.savefig('/home/theisen/www/hou_kazrge_mask.png')

# Showing how to do this for multiple radars
# Set up dictionary for profile comparison plotting
rad_dict = {'houkazrcfrgeM1.a1': {'object': ge, 'variable': variable[0]},
            'houkazrcfrmdM1.a1': {'object': md, 'variable': variable[0]},
            }

plt.clf()
# Plot up profiles and perform comparisons from data in dictionary
display = radtraq.plotting.plot_avg_profile(rad_dict)

plt.savefig('/home/theisen/www/hou_kazr_prof2.png')

# Close out object
ge.close()
md.close()
