import act
import matplotlib.pyplot as plt
import glob


files = glob.glob('/data/archive/ena/enaarmbeatmC1.c1/*2015*')
armbe = act.io.armfiles.read_netcdf(files)
armbe = act.utils.accumulate_precip(armbe, 'precip_rate_sfc')

files = glob.glob('/data/archive/ena/enametC1.b1/*2015*')
met = act.io.armfiles.read_netcdf(files)
met.clean.cleanup()
met = act.qc.arm.add_dqr_to_qc(met, variable=['pwd_precip_rate_mean_1min', 'org_precip_rate_mean'])
met.qcfilter.datafilter('pwd_precip_rate_mean_1min', rm_tests=[1,2,3,4], del_qc_var=False)
met.qcfilter.datafilter('org_precip_rate_mean', rm_tests=[1,2,3,4], del_qc_var=False)


met = act.utils.accumulate_precip(met, 'pwd_precip_rate_mean_1min')
met = act.utils.accumulate_precip(met, 'org_precip_rate_mean')

files = glob.glob('/data/archive/ena/enaldC1.b1/*2015*')
ld = act.io.armfiles.read_netcdf(files)
ld = act.utils.accumulate_precip(ld, 'precip_rate')

files = glob.glob('/data/archive/ena/enarainwbC1.b1/*2015*')
wb = act.io.armfiles.read_netcdf(files)
wb.qcfilter.datafilter('precip_rate', rm_tests=[1,2,3,4], del_qc_var=False)
wb = act.utils.accumulate_precip(wb, 'precip_rate')


display = act.plotting.TimeSeriesDisplay({'ARMBE': armbe, 'MET': met, 'LD': ld, 'WB': wb}, figsize=(12,8))
display.plot('org_precip_rate_mean_accumulated', dsname='MET', label='ORG')
display.plot('pwd_precip_rate_mean_1min_accumulated', dsname='MET', label='PWD')
display.plot('precip_rate_accumulated', dsname='LD', label='LDIS')
display.plot('precip_rate_accumulated', dsname='WB', label='WB-Gen1')
display.plot('precip_rate_sfc_accumulated', dsname='ARMBE', label='ARMBE')
display.set_yrng([0,1000])
plt.legend()
plt.savefig('/home/theisen/www/enaarmbe_comp_accumulated.png')
