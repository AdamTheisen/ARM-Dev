import glob
import xarray as xr


files = glob.glob('/data/datastream/anx/anxgensetM1.a1/*nc')

obj = xr.open_mfdataset(files)
obj = obj.sortby('time')
obj = obj.resample(time='1min', keep_attrs=True).ffill()

obj = obj.drop('time_offset')
obj = obj.drop('base_time')
obj = obj.drop('lat')
obj = obj.drop('lon')
obj = obj.drop('alt')

df = obj.to_dataframe()
df = df.fillna(0.)
print(dir(df))
df.to_csv('./genset.csv')
