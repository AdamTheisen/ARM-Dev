import act
import glob
import matplotlib.pyplot as plt
import datetime
import numpy as np
import xarray as xr

met_files = glob.glob('/data/archive/mao/maometM1.b1/*.2015*')
met_files.sort()
aosmet_files = glob.glob('/data/archive/mao/maoaosmetS1.a1/*.2015*')
aosmet_files.sort()
mwr3c_files = glob.glob('/data/archive/mao/maomwr3cM1.b1/*.2015*')
mwr3c_files.sort()
aeri_files = glob.glob('/data/archive/mao/maoaeriengineerM1.b1/*.2015*')
aeri_files.sort()

met = act.io.armfiles.read_netcdf(met_files)
met = act.qc.arm.add_dqr_to_qc(met, variable='temp_mean')
met = met.where(met['qc_temp_mean'] == 0)
met = met.resample(time='1min').nearest()

aosmet = act.io.armfiles.read_netcdf(aosmet_files)
aosmet = act.qc.arm.add_dqr_to_qc(aosmet, variable='T_Ambient')
aosmet = aosmet.where(aosmet['qc_T_Ambient'] == 0)
aosmet = aosmet.resample(time='1min').nearest()

mwr3c = act.io.armfiles.read_netcdf(mwr3c_files)
mwr3c = act.qc.arm.add_dqr_to_qc(mwr3c, variable='surface_temperature')
mwr3c = mwr3c.where(mwr3c['qc_surface_temperature'] == 0)
mwr3c = mwr3c.resample(time='1min').nearest()

aeri = act.io.armfiles.read_netcdf(aeri_files)
aeri = act.qc.arm.add_dqr_to_qc(aeri, variable='outsideAirTemp')
try:
    aeri = aeri.where(aeri['qc_outsideAirTemp'] == 0)
except:
    pass
aeri = aeri.resample(time='1min').nearest()
aeri['outsideAirTemp'].values = aeri['outsideAirTemp'].values - 273.15

#ecor = act.io.armfiles.read_netcdf(ecor_files)
test = xr.merge([met, aosmet, mwr3c, aeri], compat='override')
print(np.nanmean(test['temp_mean'].values - test['T_Ambient'].values))
print(np.nanmean(test['temp_mean'].values - test['surface_temperature'].values))
print(np.nanmean(test['temp_mean'].values - test['outsideAirTemp'].values))

#print(np.nanmean(test['temp_mean'].values - (test['mean_t'].values - 273.15)))

display = act.plotting.TimeSeriesDisplay({'MET': met, 'AOSMET': aosmet, 'MWR3C': mwr3c, 'AERI': aeri})
display.plot('outsideAirTemp', dsname='AERI', label='aeri')
display.plot('temp_mean', dsname='MET', label='met')
display.plot('T_Ambient', dsname='AOSMET', label='aosmet')
display.plot('surface_temperature', dsname='MWR3C', label='mwr3c')

display.set_yrng([0, 40])
plt.legend()
plt.savefig('/home/theisen/www/mao_met_aosmet.png')
