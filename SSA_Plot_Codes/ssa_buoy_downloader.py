# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: Sea Salt Buoy Downloader
# Author: Chung Taing
# Date Updated: 06 April 2020
# Description: This script downloads buoy data from the Mokapu Point buoy (PacIOOS Wave Buoy 098).
# =================================================================================================
# =================================================================================================
# =================================================================================================

# import packages
import datetime as dt
import netCDF4
import numpy as np
import os
import pandas as pd

# define directories
miniGNI_dir = 'C:/Users/ntril/Dropbox/mini-GNI'
data_dir = miniGNI_dir + '/python_scripts/data' 

# =================================================================================================
# =================================================================================================
# =================================================================================================
# DOWNLOAD BUOY DATA from https://cdip.ucsd.edu/themes/cdip?pb=1&u2=s:098:st:1&d2=p9
# =================================================================================================
# define the station number that you want here
stn = '098'
# define buoy deployment number if using archived dataset
deploy_num = '18'

# =================================================================================================
# THIS SECTION IS FOR GRABBING DATA FROM URL
# pick from realtime or archived dataset
# uncomment the URL that you want to use

# reading data from CDIP Archived Dataset URL
# CDIP Realtime Dataset URL
dataUrl = 'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/realtime/' + stn + 'p1_rt.nc'

# at some point in the future, will need to access archived data too
# CDIP Archived Dataset URL
#dataUrl = 'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/' + stn + 'p1/' + stn + 'p1_d' + deploy_num + '.nc'

# getting dataset
nc = netCDF4.Dataset(dataUrl)
# =================================================================================================
# THIS SECTION IS FOR READING FROM DATA FILE
#nc_filepath = data_dir + '/' + stn + 'p1_rt.nc'
#nc = netCDF4.Dataset(nc_filepath)
# =================================================================================================

# extract data of variables that I want from the NetCDF file
nc_time = nc.variables['gpsTime'][:] # date and time
time_all = [dt.datetime.fromtimestamp(t) for t in ncTime] # date and time
Hs = nc.variables['waveHs'][:] # significant wave height
Tp = nc.variables['waveTp'][:] # peak period
Ta = nc.variables['waveTa'][:] # average period
Dp = nc.variables['waveDp'][:] # peak direction
sst = nc.variables['sstSeaSurfaceTemperature'][:] # sea surface temperature

# create pandas data frame using these variables
waveDF = pd.DataFrame(list(zip(time_all, Hs, Tp, Ta, Dp, sst)), columns = ['timedate', 'wave_height', 'peak_period', 'mean_period', 'peak_dir', 'sst'])
waveDF.timedate -= dt.timedelta(hours=10) # convert from UTC to HST time zone
waveDF.to_csv(datadir + '/buoy' + str(stn) + '_data.csv', index=False, header=True)
