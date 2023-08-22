import act
import glob
import matplotlib.pyplot as plt

results = glob.glob('/data/datastream/epc/epckazrcfrgeM1.a1/*.20230819*')
results += glob.glob('/data/datastream/epc/epckazrcfrgeM1.a1/*.2023082*')
ds_kazr = act.io.armfiles.read_netcdf(results)
ds_kazr = ds_kazr.resample(time='1min').nearest()

results = glob.glob('/data/datastream/epc/epcmetM1.b1/*.20230819*')
results += glob.glob('/data/datastream/epc/epcmetM1.b1/*.2023082*')
ds_met = act.io.armfiles.read_netcdf(results)
ds_met = act.utils.accumulate_precip(ds_met, 'tbrg_precip_total')

results = glob.glob('/data/datastream/epc/epcirtsstM1.b1/*.20230819*')
results += glob.glob('/data/datastream/epc/epcirtsstM1.b1/*.2023082*')
ds_irt = act.io.armfiles.read_netcdf(results)
ds_irt = ds_irt.resample(time='1min').nearest()
print('Calc SST')
ds_irt = act.retrievals.sst_from_irt(ds_irt)

results = glob.glob('/data/datastream/epc/epcaossmpsM1.b1/*.20230819*')
results += glob.glob('/data/datastream/epc/epcaossmpsM1.b1/*.2023082*')
ds_smps = act.io.armfiles.read_netcdf(results)


print('Plotting')
display = act.plotting.TimeSeriesDisplay({'kazr': ds_kazr, 'met': ds_met, 'irtsst': ds_irt, 'smps': ds_smps}, figsize=(12,16), subplot_shape=(5,))
display.plot('reflectivity', cb_friendly=True, dsname='kazr', subplot_index=(0,))
display.plot('atmos_pressure', dsname='met', subplot_index=(1,))
display.day_night_background(dsname='met', subplot_index=(1,))
title='Air (orange) and Sea Surface Temperature'
display.plot('temp_mean', dsname='met', subplot_index=(2,), color='orange', label='Surface Temp', set_title=title)
display.axes[2].yaxis.label.set_color('orange')
display.plot('sea_surface_temperature', dsname='irtsst', subplot_index=(2,), secondary_y=True, label='Sea Surface Temp')
display.day_night_background(dsname='irtsst', subplot_index=(2,))
display.plot('tbrg_precip_total_accumulated', dsname='met', subplot_index=(3,), color='orange')
display.day_night_background(dsname='met', subplot_index=(3,))
display.plot('dN_dlogDp', dsname='smps', subplot_index=(4,))
display.set_yrng([0,500], subplot_index=(4,))
plt.legend()
plt.savefig('/data/www/userplots/theisen/hilary/data.png')
