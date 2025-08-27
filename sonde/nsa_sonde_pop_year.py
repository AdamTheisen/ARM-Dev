import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import matplotlib.pyplot as plt
import osgeo.osr as osr
import glob
import act
import xarray as xr
import numpy as np
import sys
from datetime import datetime as dt
from datetime import timedelta

current_year = dt.now().year
dates = [str(current_year)]

# Set up our limits for the image centering on central latitude and longitude
site = 'nsa'
clat = 71.323
clon = -156.615
east = clon + 8.0
west = clon - 2.5
north = clat + 1.5
south = clat - 3.

for d in dates:
    # Get SONDE Data
    files = glob.glob('/data/archive/' + site + '/' + site + 'sondewnpn*1.b1/*.' + d + '*.*.cdf')
    files.sort()
    sonde = []
    sample = None
    ds = None
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
        continue

    # Set extents to match limits
    fig = plt.figure(figsize=(14, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([west, east, south, north], ccrs.PlateCarree())

    # Grab google satellite background
    google = cimgt.GoogleTiles(style='satellite')
    ax.add_image(google, 10)

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

    plt.title(site.upper() + ' Radiosonde Termination Locations for ' + str(current_year))

    # Save the figure
    plt.tight_layout()
    plt.savefig('/data/www/userplots/theisen/' + site + '/' + site + 'sondewnpn/' + site + '_sonde_location_' + d + '.png')
