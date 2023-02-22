import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates
import numpy as np
import sys

ds = 'nsametC1.b1'
site = ds[0:3]
files = glob.glob('/data/archive/'+site+'/'+ds+'/'+ds+'.*cdf')
years = [f.split('.')[-3][0:4] for f in files]
years = np.unique(years)

for y in years:
    files = glob.glob('/data/archive/'+site+'/'+ds+'/'+ds+'.'+y+'*cdf')
    files.sort()
    #try:
    obj = act.io.armfiles.read_netcdf(files)
    obj = act.qc.arm.add_dqr_to_qc(obj, variable='temp_mean')
    obj = obj.where(obj['qc_temp_mean'] == 0)
    count = obj.resample(time='M', skipna=True).count()
    obj = obj.resample(time='M', skipna=True).mean()
    #print(obj['time'].values, obj['temp_mean'].values)
    for i in range(len(obj['time'].values)):
        print(','.join([str(obj['time'].values[i]), str(obj['temp_mean'].values[i]), str(count['temp_mean'].values[i])]))
    obj.close()
    #except:
    #    continue
