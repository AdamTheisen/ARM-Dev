import act
import glob
import matplotlib.pyplot as plt

files = glob.glob('/data/datastream/kcg/kcgccn100X30.a1/*')
files.sort()
sdate = act.utils.DatastreamParserARM(files[0]).date
edate = act.utils.DatastreamParserARM(files[-1]).date

dates = act.utils.dates_between(sdate, edate)
for d in dates:
    fdate = d.strftime('%Y%m%d')
    f = glob.glob('/data/datastream/kcg/kcgccn100X30.a1/*.' + fdate + '*')
    if len(f) == 0:
        continue
    ds = act.io.read_arm_netcdf(f)
    ds = ds.where(ds['N_CCN'] > 0.)

    f = glob.glob('/data/datastream/kcg/kcgaosuhsasS3.b1/*.' + fdate + '*')
    if len(f) == 0:
        continue
    ds_uhsas = act.io.read_arm_netcdf(f)
    
    display = act.plotting.TimeSeriesDisplay({'ccn': ds, 'uhsas': ds_uhsas}, figsize=(10,14), subplot_shape=(4,))
    display.plot('N_CCN_dN', subplot_index=(0,), dsname='ccn', vmax=100, norm='log')
    display.plot('N_CCN', subplot_index=(1,), dsname='ccn')
    display.plot('total_N_conc', subplot_index=(1,), dsname='uhsas')
    display.day_night_background(subplot_index=(1,), dsname='ccn')
    display.plot('dN_dlogDp', subplot_index=(2,), dsname='uhsas', vmax=500, norm='log')
    display.plot('CCN_supersaturation_set_point', subplot_index=(3,), dsname='ccn')
    plt.savefig('/data/www/userplots/theisen/kcg/kcgccn100X30.a1/kcgccn100X30.'+ fdate + '.png')
    plt.close()
