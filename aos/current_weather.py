import act
import glob
import datetime as dt
import pandas as pd
import numpy as np


# Information from PM report.  Time might be tricky
site = 'sgp'
fac = 'E13'
date = '20211103'
time = '1325'

# If time is 3 digits, add leading 0
if len(time) == 3:
    time = '0' + time

# Convert to PM timestamp
timestamp = dt.datetime.strptime(date + ':' + time, '%Y%m%d:%H%M')

# Get filenames for the day
aosmet_files = glob.glob(''.join(['/data/datastream/', site, '/', site, 'aosmet', fac, '.a1/*', date, '*']))
met_files = glob.glob(''.join(['/data/datastream/', site, '/', site, 'met', fac, '.b1/*', date, '*']))
# Special case for SGP
if site == 'sgp':
   fac = 'C1'
tsi_files = glob.glob(''.join(['/data/datastream/', site, '/', site, 'tsiskycover', fac, '.b1/*', date, '*']))

# Read in files using ACT
aosmet = act.io.armfiles.read_netcdf(aosmet_files)
# Calculate accumulated rainfall
aosmet = act.utils.accumulate_precip(aosmet, 'rain_intensity')
met = act.io.armfiles.read_netcdf(met_files)
# Get present weather
met = act.utils.decode_present_weather(met, variable='pwd_pw_code_1hr', decoded_name='weather')
tsi = act.io.armfiles.read_netcdf(tsi_files)
# Screen out bad TSI values
tsi = tsi.where(tsi['solar_altitude'] > 10, drop=True)

# Select time nearest to PM time
aosmet = aosmet.sel(time=timestamp, method='nearest', tolerance=dt.timedelta(minutes=10))
met = met.sel(time=timestamp, method='nearest', tolerance=dt.timedelta(minutes=10))
tsi = tsi.sel(time=timestamp, method='nearest', tolerance=dt.timedelta(minutes=60))

# Print weather report - This information would go into DB
print('Weather Report for ' + date + ' at ' + time + 'UTC')
print('Conditions for past hour: ', met['weather'].values)
print('Sky Cover %: ', tsi['percent_opaque'].values + tsi['percent_thin'].values)
print('TEMP: ', np.round(aosmet['temperature_ambient'].values, decimals=2), aosmet['temperature_ambient'].attrs['units'])
print('RH: ', np.round(aosmet['rh_ambient'].values, decimals=2), aosmet['rh_ambient'].attrs['units'])
print('PRES: ', np.round(aosmet['pressure_ambient'].values, decimals=2), aosmet['pressure_ambient'].attrs['units'])
print('WS: ', np.round(aosmet['wind_speed'].values, decimals=2), aosmet['wind_speed'].attrs['units'])
print('WD: ', np.round(aosmet['wind_direction'].values, decimals=2), aosmet['wind_direction'].attrs['units'])
print('Accumulated Rain: ', np.round(aosmet['rain_intensity_accumulated'].values, decimals=2), aosmet['wind_direction'].attrs['units'])
aosmet.close()
met.close()
tsi.close()
