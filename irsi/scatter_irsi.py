import glob
import act
import os
import xarray as xr
import matplotlib.pyplot as plt


year = 'b1.202105'
files = glob.glob('/data/archive/sgp/sgpirsiirC1.b1/*' + year + '*')
files.sort()

tsi_files = glob.glob('/data/archive/sgp/sgptsiskycoverC1.b1/*' + year + '*')
tsi_files.sort()

vis_files = glob.glob('/data/archive/sgp/sgpirsivisC1.b1/*' + year + '*')
vis_files.sort()

ds = act.io.armfiles.read_netcdf(files)
ir_variables = [
    'sky_cover_high_emission_narrow',
    'sky_cover_low_emission_narrow',
    'sky_cover_high_emission_wide',
    'sky_cover_low_emission_wide'
]
vis_variables = [
    'sky_cover_opaque_narrow',
    'sky_cover_thin_narrow',
    'sky_cover_opaque_wide',
    'sky_cover_thin_wide'
]

ds = act.qc.arm.add_dqr_to_qc(ds)
ds.qcfilter.datafilter(del_qc_var=False, rm_assessments=['Bad', 'Incorrect'])
ds = ds.resample(time='1min').nearest()

ds_tsi = act.io.armfiles.read_netcdf(tsi_files)
ds_tsi = act.qc.arm.add_dqr_to_qc(ds_tsi)
ds_tsi.qcfilter.datafilter(del_qc_var=False, rm_assessments=['Bad', 'Incorrect'])
ds_tsi = ds_tsi.resample(time='1min').nearest()

ds_vis = act.io.armfiles.read_netcdf(vis_files)
ds_vis = act.qc.arm.add_dqr_to_qc(ds_vis)
ds_vis.qcfilter.datafilter(del_qc_var=False, rm_assessments=['Bad', 'Incorrect'])
ds_vis = ds_vis.resample(time='1min').nearest()

ds_new = xr.merge([ds, ds_tsi, ds_vis], compat='override')
df = ds_new.to_dataframe()

fig, ax = plt.subplots(5, 2, figsize=(10,14))
title = 'TSI vs IRSI VIS Thin Narrow'
ax[0, 0].plot(ds_new['percent_thin'].values, ds_new['sky_cover_thin_narrow'], '.')
ax[0, 0].set_title(title)
title = 'TSI vs IRSI VIS Thin Wide'
ax[0, 1].plot(ds_new['percent_thin'].values, ds_new['sky_cover_thin_wide'], '.')
ax[0, 1].set_title(title)
title = 'TSI vs IRSI VIS Opaque Narrow'
ax[1, 0].plot(ds_new['percent_opaque'].values, ds_new['sky_cover_opaque_narrow'], '.')
ax[1, 0].set_title(title)
title = 'TSI vs IRSI VIS Opaque Wide'
ax[1, 1].plot(ds_new['percent_opaque'].values, ds_new['sky_cover_opaque_wide'], '.')
ax[1, 1].set_title(title)

title = 'TSI vs IRSI IR Opaque Narrow'
ax[2, 0].plot(ds_new['percent_opaque'].values, ds_new['sky_cover_high_emission_narrow'], '.')
ax[2, 0].set_title(title)
title = 'TSI vs IRSI IR Opaque Wide'
ax[2, 1].plot(ds_new['percent_opaque'].values, ds_new['sky_cover_high_emission_wide'], '.')
ax[2, 1].set_title(title)
title = 'TSI vs IRSI IR Thin Narrow'
ax[3, 0].plot(ds_new['percent_thin'].values, ds_new['sky_cover_low_emission_narrow'], '.')
ax[3, 0].set_title(title)
title = 'TSI vs IRSI IR Thin Wide'
ax[3, 1].plot(ds_new['percent_thin'].values, ds_new['sky_cover_low_emission_wide'], '.')
ax[3, 1].set_title(title)

title = 'IRSI VIS vs IRSI IR Opaque Wide'
ax[4, 0].plot(ds_new['sky_cover_opaque_wide'].values, ds_new['sky_cover_high_emission_wide'], '.')
ax[4, 0].set_title(title)
title = 'IRSI VIS vs IRSI IR Thin Wide'
ax[4, 1].plot(ds_new['sky_cover_thin_wide'].values, ds_new['sky_cover_low_emission_wide'], '.')
ax[4, 1].set_title(title)
for a in ax:
    for b in a:
        b.set_ylim([0, 100])
        b.set_xlim([0, 100])
        b.plot([0, 100], [0, 100], 'r')

plt.subplots_adjust(bottom=0.05, top=0.975)
directory = '/data/www/userplots/theisen/irsi/'
filename = 'sgpirsiC1.scatter_' + year + '.png'
if not os.path.exists(directory):
    os.makedirs(directory)
plt.savefig(directory + filename)


