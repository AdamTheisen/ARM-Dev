import act
import pyart
import glob
import cartopy.crs as ccrs
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime as dt
import subprocess


today = dt.date.today().strftime("%Y%m%d")

files = glob.glob('/home/theisen/www/sail_radar/images/'+today+'/*')
files.sort()

for i in range(len(files)):
    f_comp = files[i].split('.')
    fdate = str(f_comp[-4])
    ftime = (f_comp[-3])

    if 'PPI_1.' not in files[i]:
        continue

    cmd = 'convert ' + files[i]
    if 'PPI_2.' in files[i+1]:
       cmd = cmd + ' ' + files[i+1]
    if 'PPI_4.' in files[i+2]:
       cmd = cmd + ' ' + files[i+2]

    directory = '/home/theisen/www/sail_radar/multi/'+fdate
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = directory + '/sailS2.00.' + fdate + '.' + ftime +'.multi.png'
    cmd = cmd + ' +append ' + filename
    os.system(cmd)

cmd = 'convert -loop 0 /home/theisen/www/sail_radar/multi/'+str(fdate)+'/*.png '
cmd = cmd + '/home/theisen/www/sail_radar/movies/' + str(fdate) + '/'+'multi_panel.gif'
if not os.path.exists('/home/theisen/www/sail_radar/movies/' + str(fdate)):
    os.makedirs('/home/theisen/www/sail_radar/movies/' + str(fdate))
os.system(cmd)
