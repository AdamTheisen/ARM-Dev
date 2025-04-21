import radtraq
import glob
import matplotlib.pyplot as plt
import numpy as np
from act.io.arm import read_arm_netcdf

files = glob.glob('/data/datastream/bnf/bnfkazr2cfrgeM1.a1/*20250411*')
ds = read_arm_netcdf(files)

files = glob.glob('/data/datastream/bnf/bnfkazr2cfrmdM1.a1/*20250411*')
ds_md = read_arm_netcdf(files)

# Resample to 1-minute to simplify processing
ds = ds.resample(time='1min').nearest()
ds_md = ds_md.resample(time='1min').nearest()

# Process cloud mask in order to properly produce average VPT profiles through cloud
ds = radtraq.proc.cloud_mask.calc_cloud_mask(ds, 'reflectivity')
ds_md = radtraq.proc.cloud_mask.calc_cloud_mask(ds_md, 'reflectivity')

# Variables to calculate average profiles
variable = ['reflectivity', 'mean_doppler_velocity']

# Create a grid to interpolate data onto - Needed for different radars
first_height = 1500.0
ygrid = np.arange(first_height, 10000, 50)

# Calculate average profiles
ds = radtraq.proc.profile.calc_avg_profile(
    ds, variable=variable, first_height=first_height, ygrid=ygrid
)
ds_md = radtraq.proc.profile.calc_avg_profile(
    ds_md, variable=variable, first_height=first_height, ygrid=ygrid
)

rad_dict = {
    'bnfkazr2cfrgeC1.b1': {'object': ds, 'variable': variable[0]},
    'bnfkazr2cfrmdC1.b1': {'object': ds_md, 'variable': variable[0]},
}

# Plot up profiles and perform comparisons from data in dictionary
display = radtraq.plotting.plot_avg_profile(rad_dict)

# Show plot
plt.savefig('/data/www/userplots/theisen/bnfkazr/20250411_profile.png')

# Close out object
ds.close()
