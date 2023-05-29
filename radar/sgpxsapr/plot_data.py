import glob
import pyart
import matplotlib.pyplot as plt
import os
import numpy as np

ds = 'sgpxsaprI4.00'
files = glob.glob('/data/datastream/sgp/' + ds + '/*maint')

for f in files:
    radar = pyart.io.read_sigmet(f)
    el = radar.elevation['data']

    display = pyart.graph.RadarDisplay(radar)
    fig = plt.figure(figsize=[7, 5])
    ax = fig.add_subplot(111)
    scan_type = radar.scan_type
    if np.nanmean(el) > 80:
        scan_type = 'vpt'
        display.plot_vpt("reflectivity", vmin=16.0, vmax=64, cmap="pyart_HomeyerRainbow")
    else:
        display.plot(
            "reflectivity", 0, vmin=-16.0, vmax=64, cmap="pyart_HomeyerRainbow"
        )

    if radar.scan_type == 'rhi':
        display.set_limits(ylim=[0, 15], ax=ax)

    file_name = '_'.join([scan_type, f.split('.')[-3]]) + '.png'

    save_dir = '/data/www/userplots/theisen/sgp/' + ds
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.savefig(save_dir + '/' + file_name)
    plt.close(fig)

files = glob.glob(save_dir + '/*ppi*png')
#os.system("ffmpeg -r -i " + save_dir + '/*ppi*png -vcodec mpeg4 -y ' + save_dir+'/ppi.mp4')

print(files)
