import act
import glob

files = glob.glob('/data/archive/sgp/sgpmmcrmomC1.b1/*.20100601*')
print(files)
ds = act.io.arm.read_arm_mmcr(files)
print(ds)
