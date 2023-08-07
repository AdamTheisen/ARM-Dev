import act
import glob
import matplotlib.pyplot as plt
import json
import numpy as np

files = glob.glob('/data/archive/sgp/sgpmetE13.b1/*.2021*')

#Read in MET data to Standard Object
obj = act.io.armfiles.read_netcdf(files)

windrose = act.plotting.WindRoseDisplay(obj,figsize=(10,8))
title = 'SGP MET Wind Rose for May 2020-2023'
windrose.plot('wdir_vec_mean','wspd_vec_mean',spd_bins=np.linspace(0, 10, 5), set_title=title)
windrose.axes[0].legend(loc=(-0.1,0.1))
plt.savefig('/data/www/userplots/theisen/sgp/sgpwind_rose.png')
