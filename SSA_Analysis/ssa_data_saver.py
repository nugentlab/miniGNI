# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: Sea Salt Aerosol Data Saver
# Author: Chung Taing
# Date Updated: 10 April 2020
# Description: This script utilizes the functions in ssa_reader_functions. It pulls size 
# distribution data from histogram files. It also pulls wind data from the Kaneohe Marine Corps
# weather station, wave data from the Mokapu Point buoy (PacIOOS Wave Buoy 098), tide data from
# Mokuoloe, HI (station ID 1612480) from NOAA CO-OPS. Finally, it processes the data: it 
# calculates the collision efficiency of each bin, finds the cut-off size for the data, and
# recalculates bins based on uncertainties in aloft wind speed measurements.
# =================================================================================================
# =================================================================================================
# =================================================================================================

# import packages
import datetime as dt
import math
import netCDF4
import numpy as np
import os
import pandas as pd
import re
from lmfit.models import ExpressionModel
from scipy import stats

# import functions
# # see the scripts for these functions to find information on what each function does
import ssa_reader_functions as rdr
import ranzwong as rw

# define directories
miniGNI_dir = 'C:/Users/ntril/Dropbox/mini-GNI'
batch_dir = miniGNI_dir + '/ssa_histo_files'
batch1_dir = batch_dir + '/Batch1'
batch1_env_dir = miniGNI_dir + '/python_scripts/data/batch1_env_files'
data_dir = miniGNI_dir + '/python_scripts/data'
vocals_dir = batch_dir + '/VOCALS'

# directories for environmental data (buoy, tide, wind)
buoy_dir = data_dir + '/buoy098_data.csv'
tide_dir = data_dir + '/tide_data.csv'
wind_dir = data_dir + '/wind_station_data.csv'

# read in the SSA data into a data frame
ssaDF = rdr.retrieve_info(data_directory=batch_dir, file_name='sli_histo_')

# this section gets variables to put into the data frame
# the function retrieve_value finds the data by looking for matching text
sample_altitude = 'Slide exposure average GPS altitude \(m\)'
sample_pressure = 'Slide exposure average pressure \(hpa\)'
sample_temperature = 'Slide exposure average temperature \(C\)'
sample_RH = 'Slide exposure average rel\. hum\. \(\%\)'
sample_windspeed = 'Slide exposure average wind speed \(m/s\)'
# get the variables
ssaDF['pressure'] = rdr.retrieve_value(sample_pressure, data_directory=batch_dir, file_name='sli_histo_')
ssaDF['altitude'] = rdr.retrieve_value(sample_altitude, data_directory=batch_dir, file_name='sli_histo_')
ssaDF['temperature'] = rdr.retrieve_value(sample_temperature, data_directory=batch_dir, file_name='sli_histo_')
ssaDF['rh'] = rdr.retrieve_value(sample_RH, data_directory=batch_dir, file_name='sli_histo_')
ssaDF['windspeed'] = rdr.retrieve_value(sample_windspeed, data_directory=batch_dir, file_name='sli_histo_')

# read in the Batch 1 info into the data frame
batchDF = rdr.retrieve_Batch1_info()
ssaDF = pd.concat([batchDF, ssaDF], ignore_index=True)

# convert temperature to Kelvin
ssaDF['temperature'] += 273.15

# read in VOCALS data
vocalsDF = rdr.retrieve_info(data_directory=vocals_dir, file_name='sli_his_')
# VOCALS variable names
vocals_altitude = 'Slide exposure GPS altitude \(m\)'
vocals_pressure = 'Slide exposure pressure     \(hpa\)'
vocals_temperature = 'Slide exposure temperature  \(degC\)'
vocals_RH = 'Slide exposure rel\. hum\.    \(\%\)'
vocals_windspeed = 'Slide exposure wind speed   \(m/s\)'
vocals_mug = 'Log-normal geometric mean radius \(micron\)'
vocals_std = 'Log-normal geometric st\.dev\.'
vocals_chi = 'Reduced chi-square'
# read in those variables
vocalsDF['pressure'] = rdr.retrieve_value(vocals_pressure, data_directory=vocals_dir, file_name='sli_his_')
vocalsDF['altitude'] = rdr.retrieve_value(vocals_altitude, data_directory=vocals_dir, file_name='sli_his_')
vocalsDF['temperature'] = rdr.retrieve_value(vocals_temperature, data_directory=vocals_dir, file_name='sli_his_')
vocalsDF['rh'] = rdr.retrieve_value(vocals_RH, data_directory=vocals_dir, file_name='sli_his_')
vocalsDF['surface_wind'] = rdr.retrieve_value(vocals_windspeed, data_directory=vocals_dir, file_name='sli_his_')
vocalsDF['windspeed'] = vocalsDF['surface_wind'] + 250 # so that collision efficiency is 100% b/c sampling done on aircraft
vocalsDF['temperature'] += 273.15
vocalsDF['gni_mug'] = rdr.retrieve_value(vocals_mug, data_directory=vocals_dir, file_name='sli_his_')
vocalsDF['gni_std'] = rdr.retrieve_value(vocals_std, data_directory=vocals_dir, file_name='sli_his_')
vocalsDF['gni_chi'] = rdr.retrieve_value(vocals_chi, data_directory=vocals_dir, file_name='sli_his_')

# =================================================================================================
# drop some samples that were bad
# =================================================================================================
# these ocean samples were flown from a kite aboard a ship
# these samples suffered from low wind conditions and inconsistent flight
ocean_samples = ['190114a1', '190114a2', '190114a3', '190114a4', '190114a5', '190116a1', '190116a2', '190116a3', '190117a1', '190117a2', '190117a3', '190117a4', '190117a5', '190117a6']
# these samples suffered from the door getting stuck during sampling
stuck_samples = ['190101a5', '190101a6', '190116a3', '190616a5', '190616a7', '190616a8', '190820a13']
# these samples have no surface wind data
no_wind_samples = ['190307a1', '190307a4', '190307a5', '190307a6', '190307a7', '190307a8', '190307a9']
# bad samples: 181024a3 and 181116a4 had no miniGNI data, 181205a3 was dropped
bad_samples = ['181024a3', '181116a4', '181205a3']
ssaDF = rdr.drop_samples(ssaDF, drop_list = ocean_samples)
ssaDF = rdr.drop_samples(ssaDF, drop_list = stuck_samples)
ssaDF = rdr.drop_samples(ssaDF, drop_list = no_wind_samples)
ssaDF = rdr.drop_samples(ssaDF, drop_list = bad_samples)
# reset the index and re-sort after dropping slides
ssaDF.reset_index(inplace=True, drop=True)
ssaDF.sort_values('id_number', inplace=True)
# =================================================================================================

# cut VOCALS data to under 650 m
#vocalsDF = vocalsDF[vocalsDF.altitude<=650]
#vocalsDF.reset_index(inplace=True, drop=True)

# add buoy, tide, and wind data
ssaDF = rdr.add_wave_data(ssaDF, buoy_dir = buoy_dir)
ssaDF = rdr.add_tide_data(ssaDF, tide_dir = tide_dir)
ssaDF = rdr.add_wind_data(ssaDF, wind_dir = wind_dir)

# remove low CE data and add cutoff data
ssaDF = rdr.remove_low_ce(ssaDF)
ssaDF = rdr.add_cutoff_conc(ssaDF, cutoff=3.9)
#vocalsDF = rdr.remove_low_ce(vocalsDF)
#vocalsDF = rdr.add_cutoff_conc(vocalsDF, cutoff=3.9)
#vocalsDF = vocalsDF[vocalsDF.cutoff_total_conc > 150]
#vocalsDF.reset_index(inplace=True, drop=True)

# add wind sensitivity data
ssaDF = rdr.add_wind_sensitivity(ssaDF, fractional_change=0.35)
ssaDF = rdr.add_low_wind_cutoff_conc(ssaDF, cutoff=4.9)

# create synthetic data combining VOCALS and SSA data
#synthDF = ssaDF.copy(deep=True)
#synthDF = rdr.add_vocals(vdf=vocalsDF, sdf=synthDF)

# add lognormal fit data
ssaDF = rdr.fit_lognormal(ssaDF)
#vocalsDF = rdr.fit_lognormal(vocalsDF)
#synthDF = rdr.fit_synth_lognormal(synthDF)

# save the data frame to CSV
ssaDF.to_csv(data_dir + '/ssaDF.csv', index=False)
#vocalsDF.to_csv(data_dir + '/vocalsDF.csv', index=False)
#synthDF.to_csv(data_dir + '/synthDF.csv', index=False)

# NOTE: ssaDF.csv must be altered manually to include surface wind speed!!!
# Personally, I edit ssaDF.csv to include surface wind speed and then save it as a new CSV file
# titled "ssaDF_final.csv" to avoid confusion and so that the CSV file containing the 
# surface wind data does not get updated automatically when running this script.
