import act

files = act.tests.sample_files.EXAMPLE_MET1
obj = act.io.armfiles.read_netcdf(files, decode_times=False, cftime_to_datetime64=False)
display = act.plotting.TimeSeriesDisplay(obj)
display.plot('time')
