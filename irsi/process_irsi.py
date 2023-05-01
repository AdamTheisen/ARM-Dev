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

ds_tsi = act.io.armfiles.read_netcdf(tsi_files)
ds_tsi = act.qc.arm.add_dqr_to_qc(ds_tsi)
ds_tsi.qcfilter.datafilter(del_qc_var=False, rm_assessments=['Bad', 'Incorrect'])

ds_vis = act.io.armfiles.read_netcdf(vis_files)
ds_vis = act.qc.arm.add_dqr_to_qc(ds_vis)
ds_vis.qcfilter.datafilter(del_qc_var=False, rm_assessments=['Bad', 'Incorrect'])

ds_new = xr.merge([ds, ds_tsi, ds_vis], compat='override')
ds_new = ds_new.resample(time='1min', skipna=True).nearest()

bins = [0., 0.5, 1., 2., 3., 4., 5., 6, 7, 8, 9, 10]
ds = ds.where(ds['sky_cover_high_emission_narrow'].values <= 10.)
print(ds['sky_cover_high_emission_narrow'].values)
display = act.plotting.HistogramDisplay(ds_new, subplot_shape=(10,), figsize=(8, 20))
for i, v in enumerate(ir_variables):
    display.plot_stacked_bar_graph(v, subplot_index=(i,), label=v, bins=bins)
for i, v in enumerate(vis_variables):
    display.plot_stacked_bar_graph(v, subplot_index=(i+4,), label=v, bins=bins)

display.plot_stacked_bar_graph('percent_opaque', subplot_index=(8,), bins=bins)
display.plot_stacked_bar_graph('percent_thin', subplot_index=(9,), bins=bins)

plt.subplots_adjust(bottom=0.05, top=0.975)

directory = '/data/www/userplots/theisen/irsi/'
filename = 'sgpirsiC1.' + year + '.png'
if not os.path.exists(directory):
    os.makedirs(directory)
plt.savefig(directory + filename)


