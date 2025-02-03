import glob
import act


files = glob.glob('/data/reproc/D240920.2/datastream/sgp/sgpaoso3E13.b0/*.202409*')
files.sort()
for f in files:
    ds = act.io.read_arm_netcdf(f)
    max_qc = ds['qc_o3'].attrs['lamp_voltage_bench_max_alarm']
    min_qc = ds['qc_o3'].attrs['lamp_voltage_bench_min_alarm']
    if max_qc != 17.:
        print(max_qc, min_qc,f)

