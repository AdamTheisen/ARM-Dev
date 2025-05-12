""" Creates a image of the Marine Parks. """
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import geopandas
import matplotlib.pyplot as plt
import osgeo.osr as osr
import glob
import act
import xarray as xr
import numpy as np
import sys
from datetime import datetime as dt
from datetime import timedelta

dates = act.utils.dates_between('20250427', '20250503')
dates = [d.strftime('%Y%m%d') for d in dates]
# Set up our limits for the image centering on central latitude and longitude
site = 'bnf'
clat = 34.342481
clon = -87.338177
east = clon + 2.0
west = clon - 0.5
north = clat + 1.
south = clat - 1.

ds = None
for d in dates:
    # Get SONDE Data
    files = glob.glob('/data/datastream/' + site + '/' + site + 'sondewnpn*1.b1/*.' + d + '*.*.cdf')
    files.sort()
    sonde = []
    sample = None
    print(d, len(files))
    for f in files:
        obj = act.io.arm.read_arm_netcdf(f)
        obj = obj.where(obj['time'] == obj['time'].values[-1], drop=True)
        if obj['lat'].values[0] == -9999 or obj['lon'].values[0] == -9999:
            continue
        if obj['lat'].values[0] > north or obj['lat'].values[0] < south or obj['lon'].values[0] > east or obj['lon'].values[0] < west:
            print(f)
            continue
        if sample is None:
            sample = obj
        if ds is None:
            ds = obj
        else:
            ds = xr.merge([ds, obj])

if ds is None:
    sys.exit()

# Read in shape file and prj file to get the projection.
shp = geopandas.read_file("/home/theisen/Code/ARM-Dev/sonde/Marine_Parks/shp_files/MarineParks.shp")

# Convert projection from meters to lat/lon
shp = shp.to_crs(4326)

# Set extents to match limits
fig = plt.figure(figsize=(14, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([west, east, south, north], ccrs.PlateCarree())

# Grab google satellite background
google = cimgt.GoogleTiles(style='satellite', cache=True)
ax.add_image(google, 10)

# Plot polygons with geopandas
shp.plot(ax=ax, alpha=0.7, color='red', zorder=1)

# Add gridlines
gl = ax.gridlines(draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

cax = ax.scatter(ds['lon'], ds['lat'], c=ds['time'].values, cmap='spring')
ax.scatter(clon, clat, marker="P", color='y')
cbar = plt.colorbar(cax)
cbar.set_label('Time', rotation=270)

# Save the figure
plt.tight_layout()
plt.savefig('/data/www/userplots/theisen/' + site + '/'+site+'sondewnpn/' + site + '_sonde_location_' + dates[-1] + '.png')
