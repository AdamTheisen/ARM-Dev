import pyart
import glob
import matplotlib.pyplot as plt
import sys
import numpy as np

files = glob.glob('/data/archive/cor/corxsacrcfrppivqcM1.b1/*')

files = sorted(files)
for f in files:
    radar = pyart.io.read_cfradial(f)

    elevation = radar.elevation['data']
    el_diff = np.diff(elevation,2)
    ind = np.where((el_diff > 0.2))[0]
    ind = np.insert(ind, 0,0)
    ind = np.append(ind, len(elevation)-1)
    sweep = []
    start = []
    end = []
    fixed_angle = []
    for i, idx in enumerate(ind[0:-1]):
        sweep.append(i)
        if ind[i] != 0:
            ind[i] += 1
        start.append(ind[i])
        end.append(ind[i+1])
        fixed_angle.append(np.nanmean(elevation[ind[i]:ind[i+1]]))

    radar.sweep_number['data'] = sweep
    radar.fixed_angle['data'] = fixed_angle
    radar.sweep_start_ray_index['data'] = start
    radar.sweep_end_ray_index['data'] = end

    if radar.elevation['data'][0] > 1:
        continue

    fname = f.split('/')
    title = 'COR XSACR '+fname[-1].split('.')[-2] + ' El: '+str(fixed_angle[0])
    fname = '.'.join(fname[-1].split('.')[0:-1])+'.png'
    display = pyart.graph.RadarDisplay(radar)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    display.plot('reflectivity', 0, vmin=-40, vmax=40., filter_transitions=False, title=title)
    plt.savefig('./images/'+fname)
    plt.close(fig=fig)
    print(fname)
