import act
import radtraq
import glob

files = glob.glob('/data/archive/hou/houkazrcfrgeM1.a1/*20220524.*')
files.sort()

obj = act.io.armfiles.read_netcdf(files)

obj = obj.resample(time='1min').nearest()

noise = radtraq.proc.cloud_mask.calc_noise_floor(obj, 'reflectivity', height_variable='range')

[print(obj['time'].values[i], v) for i, v in enumerate(noise)]
