# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: Oahu Digital Elevation Model (DEM) Plotter
# Author: Chung Taing
# Date Updated: 10 April 2020
# Description: This script plots the bathymetry and topography of the sampling site and overlays
# # the flight path of iMet-XQ2 instruments flown at the top of the kite.
# =================================================================================================
# =================================================================================================
# =================================================================================================

# import packages
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.path as mpath
import netCDF4 as nc
import numpy as np
import pandas as pd

from matplotlib.ticker import FormatStrFormatter

plt.close('all')

# define directories
miniGNI_dir = 'C:/Users/ntril/Dropbox/mini-GNI'
plot_dir = miniGNI_dir + '/python_scripts/plots'
data_dir = miniGNI_dir + '/python_scripts/data/dem_data'

# =================================================================================================
# =================================================================================================
# =================================================================================================
# NON PLOTTING FUNCTIONS ==========================================================================
# =================================================================================================

# cleans the iMet-XQ2 data sets
def clean_XQ(df):
    # only need columns that start with 'XQ-iMet-XQ'
    df = df[df.columns[pd.Series(df.columns).str.startswith('XQ-iMet-XQ')]]
    # name the columns
    df.columns = ['pressure', 'temperature', 'rh', 't_humidity', 'date', 'time', 'lon', 'lat', 'altitude', 'sat_count']
    # only want data where satellite count was at least 5
    df = df[df.sat_count >= 5]
    # creating time date data
    df['timedate'] = df.date + ' ' + df.time
    # the following is because there is a iMet-XQ2 that saves date in a slightly different way
    try:
        df.timedate = [dt.datetime.strptime(date, '%m/%d/%Y %H:%M:%S') for date in df.timedate]
    except ValueError:
        df.timedate = [dt.datetime.strptime(date, '%Y/%m/%d %H:%M:%S') for date in df.timedate]
    df.timedate = df.timedate - dt.timedelta(hours=10) # converting from UTC to HST
    df = df[df.altitude > 50] # we only want the flight path when the iMet-XQ2 was flying
    # set the timedate to index and drop date and time columns
    df.set_index('timedate', drop=True, append=False, inplace=True)
    df.drop(['date', 'time'], axis=1, inplace=True)
    df.pressure*=100 # convert pressure to Pascals
    df['t_kelvin'] = df.temperature + 273.15 # convert temperature to Kelvin
    return df

# read in the iMet-XQ2 data for a sample day and then create a flight path out of lat/lon data
def create_path(sample_day):
    xqdf = clean_XQ(pd.read_csv(data_dir + "/" + str(sample_day) + "_aloft_xq.csv"))
    merged_list = tuple(zip(xqdf.lon, xqdf.lat))
    merged_array = np.asarray(merged_list)
    return merged_array

# =================================================================================================
# =================================================================================================
# =================================================================================================
# LOADING MAP DATA AND PLOT OPTIONS/FUNCTIONS =====================================================
# =================================================================================================

# load in the topography and bathymetry map data
dem_data = nc.Dataset(data_dir + "/oahu_13_dem.nc", "r+", format="NETCDF4")

# pulling variables from NETCDF file
lat = dem_data.variables['lat'][:]
lon = dem_data.variables['lon'][:]
dem_elevation = dem_data.variables['Band1'][:]

# choose colormap
cmap=plt.cm.gist_earth

# This was to establish how big the files were.
#print(len(lat)) # equals 11233
#print(len(lon)) # equals 10801
# Spacing in latitude and longitude is 1/10800 degrees or 1/3 arc seconds or 10 meters
# It was discovered that longitude from -157.68 to -157.64 corresponds to indices 8315-8747.
# # Latitude from 21.30 to 21.34 corresponds to indices 3024-3456.
# # Longitude from -157.668 to -157.660 corresponds to indices 8445-8531.
# # Latitude from 21.31 to 21.318 corresponds to 3132-3218.

def plot_oahu(lon, lat, dem_elevation):
    plt.rcParams['figure.figsize'] = (16.0, 12.0)
    plt.rcParams.update({'font.size': 24})
    plt.contour(lon, lat, dem_elevation, levels=[0], colors='black', linewidths=3)
    levels=np.linspace(-5000,1250,251)
    h = plt.contourf(lon, lat, dem_elevation, levels=levels, cmap = cmap)
    cm = plt.colorbar()
    #cm = plt.colorbar(ticks=np.linspace(-5000,1000,13))
    cm.set_label('Elevation (m)')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.tight_layout()
    #plt.savefig(plotdir + '/lat_lon_map/eps/oahu_topography_bathymetry.eps', format='eps')
    #plt.savefig(plotdir + '/lat_lon_map/png/oahu_topography_bathymetry.png', format='png')
    plt.close('all')

def plot_section(south_lat, north_lat, west_lon, east_lon):
    lat1 = dem_data.variables['lat'][south_lat:north_lat] # constrain new lats/longs
    lon1 = dem_data.variables['lon'][west_lon:east_lon]
    dem_elevation1 = dem_data.variables['Band1'][south_lat:north_lat,west_lon:east_lon]
    plt.rcParams['figure.figsize'] = (16.0, 10.0)
    plt.rcParams.update({'font.size': 24})
    fig, ax = plt.subplots()
    plt.contour(lon1, lat1, dem_elevation1, levels=[0], colors='black', linewidths=3)
    levels = np.linspace(-10, 270, 57)
    h = plt.contourf(lon1, lat1, dem_elevation1, levels=levels, cmap=cmap)
    plt.plot(*create_path(181205).T, color='tan', linewidth=1, linestyle='-', label='181205')
    plt.plot(*create_path(190101).T, color='black', linewidth=1, linestyle='-', label='190101')
    plt.plot(*create_path(190413).T, color='black', linewidth=1, linestyle=':', label='190413')
    plt.plot(*create_path(190423).T, color='silver', linewidth=1, linestyle='-', label='190423')
    plt.plot(*create_path(190519).T, color='silver', linewidth=1, linestyle=':', label='190519')
    plt.plot(*create_path(190616).T, color='indigo', linewidth=1, linestyle='-', label='190616')
    plt.plot(*create_path(190731).T, color='indigo', linewidth=1, linestyle=':', label='190731')
    plt.plot(*create_path(190815).T, color='maroon', linewidth=1, linestyle='-', label='190815')
    plt.plot(*create_path(190820).T, color='maroon', linewidth=1, linestyle=':', label='190820')
    plt.plot(*create_path(190822).T, color='magenta', linewidth=1, linestyle='-', label='190822')
    plt.plot(*create_path(190910).T, color='magenta', linewidth=1, linestyle=':', label='190910')
    lgd = plt.legend(bbox_to_anchor=(1.25,1.0), loc='upper left')
    for lgdobj in lgd.legendHandles:
        lgdobj.set_linewidth(2.0)
    cm = plt.colorbar(ticks=np.linspace(-10, 270, 15))
    cm.set_label('Elevation (m)')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.xticks(rotation=15)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    plt.tight_layout()
    plt.savefig(plotdir + '/lat_lon_map/eps/sample_site_' + str(south_lat) + '_' + str(west_lon) + '.eps', format='eps')
    plt.savefig(plotdir + '/lat_lon_map/png/sample_site_' + str(south_lat) + '_' + str(west_lon) + '.png', format='png')
    plt.close('all')

# =================================================================================================
# PLOTS ===========================================================================================
# =================================================================================================
if False:
    plot_oahu(lon=lon, lat=lat, dem_elevation=dem_elevation)
    plot_section(south_lat=3024, north_lat=3456, west_lon=8315, east_lon=8747)
    plot_section(south_lat=3132, north_lat=3218, west_lon=8445, east_lon=8531)

