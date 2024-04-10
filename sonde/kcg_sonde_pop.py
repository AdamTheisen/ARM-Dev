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

current_month = dt.now().month
current_year = dt.now().year
prev_month = current_month - 1
prev_year = current_year
if prev_month < 1:
    prev_month = 12
    prev_year = current_year - 1
dates = [str(current_year) + str(current_month).zfill(2), str(prev_year) + str(prev_month).zfill(2)]
current_days = dt.now().day
if current_days >= 5:
    dates = [dates[0]]

# Set up our limits for the image centering on central latitude and longitude
site = 'kcg'
clat = -40.6808
clon = 144.69
east = clon + 4.5
west = clon - 2.5
north = clat + 1.5
south = clat - 3.

for d in dates:
    # Get SONDE Data
    files = glob.glob('/data/datastream/' + site + '/' + site + 'sondewnpn*1.b1/*.' + d + '*.*.cdf')
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
    shp.plot(ax=ax, alpha=0.7, color='red', zorder=10)

    # Add gridlines
    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    cax = ax.scatter(ds['lon'], ds['lat'], c=ds['time'].values, cmap='YlOrRd')
    ax.scatter(clon, clat, marker="P", color='y')
    cbar = plt.colorbar(cax)
    cbar.set_label('Time', rotation=270)

    # Save the figure
    plt.tight_layout()
    plt.savefig('/data/www/userplots/theisen/' + site + '/kcgsondewnpn/' + site + '_sonde_location_' + d + '.png')
