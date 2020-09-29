# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: Environment File Generator
# Author: Chung Taing
# Date Updated: 13 April 2020
# Description: This script generates environment files for each sample. The GNI microscope software
# # requires these files to compute number concentration after counting the amount of SSA on the
# # sampling slide.
# =================================================================================================
# =================================================================================================
# =================================================================================================

# import packages and functions
import datetime as dt
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

import miniGNI_functions as mgf

# define directories
miniGNI_dir = 'C:/Users/ntril/Dropbox/mini-GNI'
flight_dir = miniGNI_dir + '/miniGNI_data'

# DEFINE VALUES HERE ==============================================================================

# specify which mini-GNI you want to generate slide environment files for
gni_number = '5' # must be a 1 digit number as a string

# define the year, month, day, hour, and minute when the sampling day began
sample_year = '2019' # 4 digit year, must be string
sample_month = '09' # 2 digit month, must be string
sample_day = '10' # 2 digit day, must be string
sample_hour = '09' # 2 digit hour from 0-24, no AM/PM, must be string
sample_minute = '00' # 2 digit minute, must be string

# See miniGNI_plotter for explanation of time_corrector - it needs to be found manually through
# # plotting. It is a time correction factor to account for drift in mini-GNI real time clock.
# # Can also see the end of this script for saved values of time corrector for previous samples.
# 9/10 time corrector for miniGNI 1-5 respectively
#time_corrector = dt.timedelta(seconds=-111)
#time_corrector = dt.timedelta(seconds=-705)
#time_corrector = dt.timedelta(seconds=-237)
#time_corrector = dt.timedelta(seconds=-336)
time_corrector = dt.timedelta(seconds=73)

# Define the surface wind speeds in m/s of each sample of the mini-GNI. If a flight was invalid
# # due to some issue, then write in -1 for that sample.
windspeed_bar = [5.4, 5.1, 6.0]
windspeed_min = [3.3, 3.4, 3.0]
windspeed_max = [7.8, 6.7, 7.9]

wind_dir = 25.00 # use 2 decimal places to describe compass wind direction

# surface altitude of surface wind speed measurement
surface_height = 6

# specify longitude and latitude with TWO decimal places
lon = -157.66
lat = 21.31

# define directories
miniGNI_dir = 
flightBaseDir = 'C:/Users/Aaron/Dropbox/mini-GNI/FlightData'

# =======================================================================================

#ff.generateSliEnv(gni_number=gni_number, sample_year=sample_year, sample_month=sample_month, sample_day=sample_day, sample_hour=sample_hour, sample_minute=sample_minute, windspeed_bar=windspeed_bar, windspeed_min=windspeed_min, windspeed_max=windspeed_max, wind_dir=wind_dir, surface_height=surface_height, lon=lon, lat=lat, time_corrector=time_corrector)

ff.renameSliEnv(flightBaseDir=flightBaseDir, sample_year=sample_year, sample_month=sample_month, sample_day=sample_day)



# =================================================================================================
# SAVED TIME CORRECTOR VALUES =====================================================================
# =================================================================================================

# 9/10
#time_corrector1 = dt.timedelta(seconds=-111)
#time_corrector2 = dt.timedelta(seconds=-705)
#time_corrector3 = dt.timedelta(seconds=-237)
#time_corrector4 = dt.timedelta(seconds=-336)
#time_corrector5 = dt.timedelta(seconds=73)

# 8/22
#time_corrector1 = dt.timedelta(seconds=32)
#time_corrector2 = dt.timedelta(seconds=-562)
#time_corrector3 = dt.timedelta(seconds=-151)
#time_corrector4 = dt.timedelta(seconds=-176)
#time_corrector5 = dt.timedelta(seconds=-119)

# 8/20
#time_corrector1 = dt.timedelta(seconds=8459545)
#time_corrector2 = dt.timedelta(seconds=-546)
#time_corrector3 = dt.timedelta(seconds=-115)
#time_corrector4 = dt.timedelta(seconds=-158)
#time_corrector5 = dt.timedelta(seconds=-119)

# 8/15
#time_corrector1 = dt.timedelta(seconds=-971)
#time_corrector2 = dt.timedelta(seconds=-509)
#time_corrector3 = dt.timedelta(seconds=-92)
#time_corrector4 = dt.timedelta(seconds=-126)
#time_corrector5 = dt.timedelta(seconds=-80)

# 7/31
#time_corrector1 = dt.timedelta(seconds=-853)
#time_corrector2 = dt.timedelta(seconds=19)
#time_corrector3 = dt.timedelta(seconds=19)
#time_corrector4 = dt.timedelta(seconds=-1)

# =================================================================================================
# =================================================================================================
# =================================================================================================

