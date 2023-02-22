import act
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import matplotlib.dates as mdates

files = glob.glob('/data/archive/sgp/sgpswatsE13.b1/*cdf')
files.extend(glob.glob('/data/archive/sgp/sgpswatsE13.b1/*.nc'))
files.sort()

for f in files:
    try:
        obj = act.io.armfiles.read_netcdf(f)
        variable = 'watcont_W'
        if variable not in obj:
            variable = 'watcont_w'
        filename = f.split('/')[-1]
        filename = '.'.join(filename.split('.')[0:-1]) + '.nc'
        obj['watcont_w'] = obj[variable]
        obj['watcont_w'].to_netcdf('/home/theisen/Code/swats/data/' + filename)
    except:
        continue
