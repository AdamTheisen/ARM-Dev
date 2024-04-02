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

# Set up our limits for the image centering on central latitude and longitude
clat = -40.6808
clon = 144.69
east = clon + 2.2
west = clon - 1.6
north = clat + 1.3
south = clat - 0.9

# Get SONDE Data
files = glob.glob('/Users/atheisen/Code/development-space/data/sgpsondewnpnC1.b1/*')
files.sort()
sonde = []
sample = None
ds = None
for f in files:
    obj = act.io.arm.read_arm_netcdf(f)
    obj = obj.where(obj['time'] == obj['time'].values[-1], drop=True)
    if obj['lat'].values[0] == -9999 or obj['lon'].values[0] == -9999:
            continue
    obj['lat'].values = [-40.6808 + np.random.default_rng().random() * 1.]
    obj['lon'].values = [144.69 + np.random.default_rng().random() * 1.]
    if obj['lat'].values[0] > north or obj['lat'].values[0] < south or obj['lon'].values[0] > east or obj['lon'].values[0] < west:
        print(f)
        continue
    if sample is None:
        sample = obj
    if ds is None:
        ds = obj
    else:
        ds = xr.merge([ds, obj])

# Read in shape file and prj file to get the projection.
shp = geopandas.read_file("./Marine_Parks/shp_files/MarineParks.shp")

# Convert projection from meters to lat/lon
shp = shp.to_crs(4326)

# Set extents to match limits
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
ax.scatter(clon, clat, color='y')
cbar = plt.colorbar(cax)
cbar.set_label('Time', rotation=270)

# Save the figure
plt.show()
