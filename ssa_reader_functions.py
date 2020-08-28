# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: Sea Salt Aerosol Reader Functions
# Author: Chung Taing
# Date Updated: 10 April 2020
# Description: This script contains all the functions used to process GNI microscope data. It pulls
# # size distribution data from histogram files. It also pulls wind data from the Kaneohe Marine
# # Corps weather station, wave data from the Mokapu Point buoy (PacIOOS Wave Buoy 098), tide data
# # from Mokuoloe, HI (station ID 1612480) from NOAA CO-OPS. 
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
import ranzwong as rw
from lmfit.models import ExpressionModel
from scipy import stats

# define directories
miniGNI_dir = 'C:/Users/ntril/Dropbox/mini-GNI'
batch_dir = miniGNI_dir + '/ssa_histo_files'
batch1_dir = batch_dir + '/Batch1'
batch1_env_dir = miniGNI_dir + '/python_scripts/data/batch1_env_files'
data_dir = miniGNI_dir + '/python_scripts/data'

# directories for environmental data (buoy, tide, wind)
buoy_dir = data_dir + '/buoy098_data.csv'
tide_dir = data_dir + '/tide_data.csv'
wind_dir = data_dir + '/wind_station_data.csv'

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: retrieve_info
# Parameters: None
# Description: This pulls sample date, sample ID number, and concentration data from text files. It
# # does so by walking through files in the data directory, finding the histogram files, and then
# # searching through the histogram files to find the correct data. It then appends the data for
# # each sample to a list. Each list becomes a column in a data frame where each row represents
# # one of the samples.
# =================================================================================================
def retrieve_info(data_directory, file_name):
    # All of these lists will eventually become columns in a data frame, and each row in the 
    # # data frame is one sample. 
    id_list = [] # sample ID number
    date_list = [] # sample date
    begin_list = [] # sample beginning time
    end_list = [] # sample ending time
    duration_list = [] # sample duration
    rv_list = [] # sample Ranz-Wong 50% collision efficiency cutoff size
    bin_num_list = [] # sample label of each bin
    lower_bin_list = [] # sample lower size of each bin
    mid_bin_list = [] # sample middle point of each bin
    upper_bin_list = [] # sample upper size of each bin
    conc_list = [] # sample concentration for each bin
    cumu_conc_list = [] # sample cumulative concentration for each bin
    salt_bin_list = [] # sample salt mass for each bin
    salt_list = [] # total salt mass of each sample
    for subdir, dirs, files in os.walk(data_directory): # walking through the files in data_directory
        for file in files:
            if file.startswith(file_name): # finding the histogram files
                filepath = subdir + os.sep + file # getting the filepath
                myfile = open(filepath, 'rt') # opening the file using the filepath
                id_str = file.split(file_name,1)[1] # pulling the sample ID number from the file name
                #id_str = file[10:] # pulling the sample ID number from the file name
                id_list.append(id_str)
                # pulling the sample date
                # # The if-statement is there because the sample ID is created by combining
                # # the date and the sample number, and if there are more than 9 samples
                # # taken in one day, the sample ID will be one digit longer.
                #if len(id_str) > 8:
                #    date_str = file[10:-3]
                #else:
                #    date_str = file[10:-2]
                date_str = id_str.split('a',1)[0]
                date_list.append(dt.datetime.strptime(date_str, '%y%m%d').date())
                # getting the size and and mass distributions for each sample
                # # I have to create vectors here because EACH sample has a size distribution.
                # # This means that for each row in the data frame, the columns for size 
                # # distribution are lists of lists.
                bin_num_vector = []
                lower_bin_vector = []
                mid_bin_vector = []
                upper_bin_vector = []
                conc_vector = []
                cumu_conc_vector = []
                salt_bin_vector = []
                for line in myfile: # walking through each line of the file to find matches
                    match = re.search('\s+(\d+)\s+(\d+)\.(\d+)\s+(\d+)\.(\d+)\s+(\d+)\.(\d+)\s+\d\s+(\d)\.(\d+)E\+(\d+)', line)
                    if match: # this match gets the size distribution
                        # All this stuff means that the first number in the match is the Bin Number. The second and third
                        # # numbers in the match are the left and right side of a decimal number (e.g. 4.5). And so on.
                        bin_num_vector.append(int(match.group(1)))
                        lower_bin_vector.append(float(match.group(2) + '.' + match.group(3)))
                        mid_bin_vector.append(float(match.group(4) + '.' + match.group(5)))
                        upper_bin_vector.append(float(match.group(6) + '.' + match.group(7)))
                        # The concentration in these histogram files are in exponential notation (e.g. 1.5e5).
                        base = float(match.group(8) + '.' + match.group(9)) # gets the base of the exponential
                        exp = float(match.group(10)) # gets the exponent
                        conc_num = base * (10**exp) # calculates the number from the base and exponent
                        conc_vector.append(conc_num)
                    match_begin = re.search('Slide begin exposure\s+\(hhmmss\.s\)\s+=\s+(\d+)\.\d', line)
                    if match_begin: # this match gets the starting time of each sample
                        time_begin = dt.datetime.strptime(date_str + ' ' + match_begin.group(1), '%y%m%d %H%M%S')
                        begin_list.append(time_begin)
                    match_end = re.search('Slide end exposure\s+\(hhmmss\.s\)\s+=\s+(\d+)\.\d', line)
                    if match_end: # this match gets the ending time of each sample
                        time_end = dt.datetime.strptime(date_str + ' ' + match_end.group(1), '%y%m%d %H%M%S')
                        end_list.append(time_end)
                    match_duration = re.search('Slide exposure duration \(s\)\s+=\s+(\d+)', line)
                    if match_duration: # this match gets the duration of each sample
                        duration_list.append(float(match_duration.group(1))/60.0)
                    match_RV = re.search('Ranz-Vong 50\% coll-eff radius \(m\)\s+=\s+(\d+)\.(\d+)', line)
                    if match_RV: # this match gets the Ranz-Wong 50% collision efficiency radius of each sample
                        # it is multiplied by 1000000 to convert from meters to micrometers
                        rv_radius = 1000000*float(match_RV.group(1) + '.' + match_RV.group(2))
                        rv_list.append(rv_radius)
                # Some data files only give up to 19.4 um (middle bin) instead of 19.8 um. This
                # # is problematic because we want the data files to be consistent for analysis
                # # purposes. Therefore, lower_bin, middle_bin, upper_bin, and concentration
                # # are extended to 19.8 um (concentration set to 0 for the extended values).
                if max(mid_bin_vector) < 19.8:
                    bin_num_vector.append(98)
                    bin_num_vector.append(99)
                    lower_bin_vector.append(19.5)
                    lower_bin_vector.append(19.7)
                    mid_bin_vector.append(19.6)
                    mid_bin_vector.append(19.8)
                    upper_bin_vector.append(19.7)
                    upper_bin_vector.append(19.9)
                    conc_vector.append(0.0)
                    conc_vector.append(0.0)
                # This calculates the salt mass in ug from the radius using (4/3)pi*r^3.
                # # The total salt mass for each bin is calculcated, and then the total salt mass
                # # for the entire sample is calculcated. The radius used is the midpoint of each 
                # # bin in microns. NaCl density is 2170 kg*m-3.
                for r, n in zip(mid_bin_vector, conc_vector):
                    salt_bin_vector.append((4*math.pi*((r/1000000)**3)/3)*2170*1000000000*n)
                salt_bin_list.append(salt_bin_vector) # salt mass of each bin for each sample
                salt_list.append(sum(salt_bin_vector)) # total salt mass for each sample
                # The following few lines calculates the cumulative concentration for each sample.
                # # The cumulative concentration can be thought of as "the total concentration of
                # # all SSA with dry radius larger than X." For example, for a size range of 2-16
                # # microns radius, the value at 5 microns is the number concentration of all
                # # SSA particles with 5-16 microns radius.
                conc_series = pd.Series(conc_vector)
                cumu_conc_series = conc_series[::-1].cumsum()[::-1] # cumulative concentration
                cumu_conc_vector = cumu_conc_series.tolist()
                cumu_conc_list.append(cumu_conc_vector)
                # Now I am just appending the vectors I filled above into the lists.
                bin_num_list.append(bin_num_vector)
                lower_bin_list.append(lower_bin_vector)
                mid_bin_list.append(mid_bin_vector)
                upper_bin_list.append(upper_bin_vector)
                conc_list.append(conc_vector)
    total_conc_list = list(map(sum, conc_list)) # total concentration of each sample
    infoDF = pd.DataFrame() # creating the data frame
    # Here I define the variable names for each column and put the lists into the columns
    # # of a data frame "infoDF" which is then returned as the output of this function.
    infoDF['id_number'] = pd.Series(id_list)
    infoDF['date'] = pd.Series(date_list)
    infoDF['timedate'] = pd.Series(begin_list)
    infoDF['end_time'] = pd.Series(end_list)
    infoDF['duration'] = pd.Series(duration_list)
    infoDF['rv_radius'] = pd.Series(rv_list)
    infoDF['bin_number'] = pd.Series(bin_num_list)
    infoDF['bin_lower'] = pd.Series(lower_bin_list)
    infoDF['bin_middle'] = pd.Series(mid_bin_list)
    infoDF['bin_upper'] = pd.Series(upper_bin_list)
    infoDF['bin_conc'] = pd.Series(conc_list)
    infoDF['cumu_conc'] = pd.Series(cumu_conc_list)
    infoDF['total_conc'] = pd.Series(total_conc_list)
    infoDF['bin_salt'] = pd.Series(salt_bin_list)
    infoDF['total_salt'] = pd.Series(salt_list)
    return infoDF

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: retrieve_Batch1_info
# Parameters: None
# Description: This pulls sample date, sample ID number, and concentration data from text files. It
# # does so by walking through files in the data directory, finding the histogram files, and then
# # searching through the histogram files to find the correct data. This is different from
# # retrieve_info because the Batch 1 files have a different format. The Batch 1 files do not have
# # all the information the other histogram files have, so we must also walk through a directory
# # of environmental data files to obtain certain variables.
# =================================================================================================
def retrieve_Batch1_info():
    # These lists will eventually become the columns in a data frame.
    id_list = [] # sample id number
    rv_list = [] # sample ranz wong 50% collision efficiency cut off radius
    bin_num_list = [] # sample number of each bin
    lower_bin_list = [] # sample lower size of each bin 
    mid_bin_list = [] # sample middle point of each bin
    upper_bin_list = [] # sample upper size of each bin
    conc_list = [] # sample concentration of each bin
    total_conc_list = [] # sample total concentration
    cumu_conc_list = [] # sample cumulative concentration of each bin
    salt_bin_list = [] # sample salt mass of each bin
    salt_list = [] # sample total salt mass
    ignore = False # I define this here outside of the for-loop that I will use it in.
    for subdir, dirs, files in os.walk(batch1_dir): # walking through the batch1_dir directory
        for file in files:
            if file.startswith('sea_salt_spectrum'): # finding files called "sea_salt_spectrum"
                ignore = False # I set this to the default value of False.
                filepath = subdir + os.sep + file # get the file path
                id_list.append(file[18:]) # pull the sample ID from the file name
                myfile = open(filepath, 'rt') # open the file
                # getting the size and and mass distributions for each sample
                # # I have to create vectors here because EACH sample has a size distribution.
                # # This means that for each row in the data frame, the columns for size 
                # # distribution are lists of lists.
                bin_num_vector = []
                lower_bin_vector = []
                mid_bin_vector = []
                upper_bin_vector = []
                conc_vector = []
                cumu_conc_vector = []
                salt_bin_vector = []
                for line in myfile: # go through each line of the file
                    match = re.search('\s+(\d+)\s+(\d+)\.(\d+)\s+(\d+)\.(\d+)\s+(\d+)\.(\d+)\s+\d\.\d+E\+\d+\s+\d\.\d+E\+\d+\s+(\d)\.(\d+)E\+(\d+)\s+(\d)\.(\d+)E\+(\d+)', line)
                    if match: # this match gets the size distribution
                        # Here is where the "ignore" variable comes into play. What is happening
                        # # here is that I want the results from here to match the format of the
                        # # results I pull from the histogram files using the function
                        # # retrieve_info(). Those histogram files only concern the size
                        # # distribution from 0.8 to 19.8 microns. I therefore instruct this
                        # # function to ignore a line if the bin mid point is less than 0.8 or
                        # # greater than 19.8 microns. The concentrations at those sizes should
                        # # be 0 anyway due to either too low collision efficiency for the 
                        # # small sizes (<0.8) or due to simply almost none being in the
                        # # atmosphere for large sizes (>19.8). 
                        mid_bin_num = float(match.group(4) + '.' + match.group(5))
                        if mid_bin_num > 19.80 or mid_bin_num < 0.8 :
                            ignore = True
                        else:
                            ignore = False
                        if ignore == False:
                            # This means that the first number is the bin number. The second and
                            # # third numbers are the lower size limit of each bin. And so on.
                            bin_num_vector.append(int(match.group(1)))
                            lower_bin_vector.append(float(match.group(2) + '.' + match.group(3)))
                            mid_bin_num = float(match.group(4) + '.' + match.group(5))
                            mid_bin_vector.append(mid_bin_num)
                            upper_bin_vector.append(float(match.group(6) + '.' + match.group(7)))
                            # The concentration and cumulative concentrations are listed in 
                            # # exponential notation. I therefore have to calculate it using the
                            # # base and exponent I read from the file.
                            base1 = float(match.group(8) + '.' + match.group(9))
                            exp1 = float(match.group(10))
                            base2 = float(match.group(11) + '.' + match.group(12))
                            exp2 = float(match.group(13))
                            conc_vector.append(base1*(10**exp1))
                            cumu_conc_vector.append(base2*(10**exp2))
                    if ignore == False:
                        match_RV = re.search(' cumulative: ranz_wong_50_percent=\s+(\d)\.(\d+)E\-(\d+)', line)
                        if match_RV: # this match gets the ranz wong 50% collision efficiency cutoff
                            rv_base = float(match_RV.group(1) + '.' + match_RV.group(2))
                            rv_exp = float(match_RV.group(3))
                            # convert from meters to micrometers
                            rv_list.append(1000000*rv_base*(10**(-1*rv_exp)))
                # calculate the salt mass for each bin
                for r, n in zip(mid_bin_vector, conc_vector):
                    salt_bin_vector.append((4*math.pi*((r/1000000)**3)/3)*2170*1000000000*n)
                # Now I am just appending the vectors I filled above into the lists
                salt_bin_list.append(salt_bin_vector)
                salt_list.append(sum(salt_bin_vector))
                cumu_conc_list.append(cumu_conc_vector)
                bin_num_list.append(bin_num_vector)
                lower_bin_list.append(lower_bin_vector)
                mid_bin_list.append(mid_bin_vector)
                upper_bin_list.append(upper_bin_vector)
                conc_list.append(conc_vector)
    # getting the total concentration
    total_conc_list = list(map(sum, conc_list))
    # Now I go to environmental files to get the following variables.
    date_list = [] # sample date
    begin_list = [] # sample beginning time
    end_list = [] # sample ending time
    duration_list = [] # sample duration
    wind_list = [] # sample wind speed
    rh_list = [] # sample relative humidity
    temp_list = [] # sample temperature
    alt_list = [] # sample altitude
    pressure_list = [] # sample pressure
    # walking through the environmental files
    for subdir, dirs, files in os.walk(batch1_env_dir):
        for file in files:
            # finding files that start with "sli_ev" and checks that the sample ID in the file
            # # name matches one of the sample IDs that we collected earlier in this function.
            if file.startswith('sli_env') and file[8:] in id_list:
                date_str = file[8:-2] # pull the date from the file name
                date_list.append(dt.datetime.strptime(date_str, '%y%m%d').date())
                filepath = subdir + os.sep + file # get the file path
                myfile = open(filepath, 'rt') # open the file
                for line in myfile: # go through each line in the file
                    match_wind = re.search('\s+(\d+)\.(\d+)\s+wind_speed_bar', line)
                    if match_wind: # this match gets the wind speed
                        wind_list.append(float(match_wind.group(1) + '.' + match_wind.group(2)))
                    match_alt = re.search('\s+(\d+)\.\s+z_bar', line)
                    if match_alt: # this match gets the altitude
                        alt_list.append(int(match_alt.group(1)))
                    match_RH = re.search('\s+(\d)\.(\d+)\s+rel_hum_bar', line)
                    if match_RH: # this match gets the relative humidity
                        rh_list.append(100*float(match_RH.group(1) + '.' + match_RH.group(2)))
                    match_P = re.search('\s+(\d+)\.\s+p_bar', line)
                    if match_P: # this match gets the pressure
                        pressure_list.append(float(match_P.group(1))/100)
                    match_T = re.search('\s+(\d+)\.(\d+)\s+t_bar', line)
                    if match_T: # this match gets the temperature
                        temp_list.append(float(match_T.group(1) + '.' + match_T.group(2)) - 273.15)
                    match_begin = re.search('\s+(\d+)\.\d\s+hhmmss_begin', line)
                    if match_begin: # this match gets the beginning time
                        t_begin = dt.datetime.strptime(date_str + ' ' + match_begin.group(1), '%y%m%d %H%M%S')
                        begin_list.append(t_begin)
                    match_end = re.search('\s+(\d+)\.\d\s+hhmmss_end', line)
                    if match_end: # this match gets the ending time
                        t_end = dt.datetime.strptime(date_str + ' ' + match_end.group(1), '%y%m%d %H%M%S')
                        end_list.append(t_end)
                # this calculates the duration by subtracting ending time from beginning time
                t_diff = (t_end - t_begin).total_seconds()/60.0
                duration_list.append(t_diff)
    # now create the data frame
    infoDF = pd.DataFrame()
    # the columns of the data frame are the lists created
    infoDF['id_number'] = pd.Series(id_list)
    infoDF['date'] = pd.Series(date_list)
    infoDF['timedate'] = pd.Series(begin_list)
    infoDF['end_time'] = pd.Series(end_list)
    infoDF['duration'] = pd.Series(duration_list)
    infoDF['rv_radius'] = pd.Series(rv_list)
    infoDF['bin_number'] = pd.Series(bin_num_list)
    infoDF['bin_lower'] = pd.Series(lower_bin_list)
    infoDF['bin_middle'] = pd.Series(mid_bin_list)
    infoDF['bin_upper'] = pd.Series(upper_bin_list)
    infoDF['bin_conc'] = pd.Series(conc_list)
    infoDF['cumu_conc'] = pd.Series(cumu_conc_list)
    infoDF['total_conc'] = pd.Series(total_conc_list)
    infoDF['bin_salt'] = pd.Series(salt_bin_list)
    infoDF['total_salt'] = pd.Series(salt_list)
    infoDF['pressure'] = pd.Series(pressure_list)
    infoDF['altitude'] = pd.Series(alt_list)
    infoDF['temperature'] = pd.Series(temp_list)
    infoDF['rh'] = pd.Series(rh_list)
    infoDF['windspeed'] = pd.Series(wind_list)
    return infoDF

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: retrieve_value
# Parameters: info_label
# Description: This pulls a specific variable from histogram files into the data frame. The
# variable is chosen by info_label, which is the text that the function can identify in the
# histogram file in order to pull the variable's data.
# =================================================================================================
def retrieve_value(info_label, data_directory, file_name):
    info_list = [] # initializes the list
    # walks through the directory
    for subdir, dirs, files in os.walk(data_directory):
        for file in files:
            if file.startswith(file_name): # opens histogram files
                filepath = subdir + os.sep + file # gets the file path
                myfile = open(filepath, 'rt') # opens the file
                for line in myfile: # looks through the lines of the file
                    match = re.search(info_label + '\s+=\s+(\d+)\.(\d+)', line)
                    if match: # finds the match for the variable that you want
                        info_list.append(float(match.group(1) + '.' + match.group(2)))
    return info_list

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: add_buoy_data
# Parameters: df, buoy_dir
# Description: This adds buoy data to the data frame.
# =================================================================================================
def add_wave_data(df, buoy_dir):
    buoyDF = pd.read_csv(buoy_dir) # read in the buoy data
    buoyDF['timedate'] = pd.to_datetime(buoyDF['timedate'])
    # match buoy data to each sample in our sample data frame
    time_list = [] # date and time
    Hs_list = [] # significant wave height
    Tp_list = [] # peak period
    Ta_list = [] # mean period
    Dp_list = [] # peak direction
    sst_list = [] # sea surface temperature
    for row in df.itertuples(): # going through the dataframe of the samples
        begin_time = getattr(row, 'timedate') # get the beginning time of each sample
        end_time = getattr(row, 'end_time') # get the ending time of each sample
        # get the middle time point of the sample using the beginning and ending
        target_time = begin_time + (end_time - begin_time)/2
        # find the nearest buoy data point in time to the target time
        nearest_time = min(buoyDF['timedate'], key=lambda d: abs(d - target_time))
        # identifies the index in the buoy data frame for that nearest data point
        buoy_index = buoyDF.loc[buoyDF['timedate'] == nearest_time].index[0]
        # pull and get data using that index
        time_list.append(buoyDF.iloc[buoy_index]['timedate']) # buoy time
        Hs_list.append(buoyDF.iloc[buoy_index]['wave_height']) # buoy wave height
        Tp_list.append(buoyDF.iloc[buoy_index]['peak_period']) # buoy peak period
        Ta_list.append(buoyDF.iloc[buoy_index]['mean_period']) # buoy mean period
        Dp_list.append(buoyDF.iloc[buoy_index]['peak_dir']) # buoy peak direction
        sst_list.append(buoyDF.iloc[buoy_index]['sst'] + 273.15) # buoy sea surface temperature
    # create new columns in the sample data frame corresponding to the buoy data
    df['wave_time'] = pd.Series(time_list)
    df['wave_height'] = pd.Series(Hs_list)
    df['peak_period'] = pd.Series(Tp_list)
    df['mean_period'] = pd.Series(Ta_list)
    df['peak_dir'] = pd.Series(Dp_list)
    df['sst'] = pd.Series(sst_list)
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: add_wind_data
# Parameters: df, wind_dir
# Description: This adds Kaneohe Marine Corps station wind data to the data frame.
# =================================================================================================
def add_wind_data(df, wind_dir):
    windDF = pd.read_csv(wind_dir) # read in wind data
    windDF['timedate'] = pd.to_datetime(windDF['timedate'])
    # match weather station data to each sample in our sample data frame
    # all the wind speeds are 10-meter wind speeds
    time_list = [] # date and time
    wind_list = [] # wind speed
    wind_dir_list = [] # wind direction
    wind6hr_list = [] # average magnitude of wind speed over 6 hrs prior to the sample time
    wind12hr_list = [] # average magnitude of wind speed over 12 hrs prior to the sample time
    wind24hr_list = [] # average magnitude of wind speed over 24 hrs prior to the sample time
    wind48hr_list = [] # average magnitude of wind speed over 48 hrs prior to the sample time
    wind72hr_list = [] # average magnitude of wind speed over 72 hrs prior to the sample time
    wind120hr_list = [] # average magnitude of wind speed over 120 hrs prior to the sample time
    visibility_list = [] # the visibility at the time of the sample
    for row in df.itertuples(): # going through the data frame 
        begin_time = getattr(row, 'timedate') # get the beginning time of each sample
        end_time = getattr(row, 'end_time') # get the ending time of each sample
        # the target time is the mid point between the beginning and the ending
        target_time = begin_time + (end_time - begin_time)/2
        # this finds the nearest time in the wind data to the target time
        nearest_time = min(windDF['timedate'], key=lambda d: abs(d - target_time))
        # gets the index of the nearest time in the wind data
        wind_index = windDF.loc[windDF['timedate'] == nearest_time].index[0]
        # uses the index to get wind data corresponding to the time of samples
        time_list.append(windDF.iloc[wind_index]['timedate'])
        wind_list.append(0.44704*windDF.iloc[wind_index]['wind_speed'])
        visibility_list.append(windDF.iloc[wind_index]['visibility'])
        wind_dir_list.append(windDF.iloc[wind_index]['wind_direction'])
        # converting all wind speeds from knots to meters per second.
        wind6hr_list.append(0.44704*windDF.loc[(windDF.index<=wind_index) & (windDF.index>(wind_index-6)), 'wind_speed'].values.mean(axis=0))
        wind12hr_list.append(0.44704*windDF.loc[(windDF.index<=wind_index) & (windDF.index>(wind_index-12)), 'wind_speed'].values.mean(axis=0))
        wind24hr_list.append(0.44704*windDF.loc[(windDF.index<=wind_index) & (windDF.index>(wind_index-24)), 'wind_speed'].values.mean(axis=0))
        wind48hr_list.append(0.44704*windDF.loc[(windDF.index<=wind_index) & (windDF.index>(wind_index-48)), 'wind_speed'].values.mean(axis=0))
        wind72hr_list.append(0.44704*windDF.loc[(windDF.index<=wind_index) & (windDF.index>(wind_index-72)), 'wind_speed'].values.mean(axis=0))
        wind120hr_list.append(0.44804*windDF.loc[(windDF.index<=wind_index) & (windDF.index>(wind_index-120)), 'wind_speed'].values.mean(axis=0))
    # adding all the lists to the sample data frame
    df['phng_time'] = pd.Series(time_list)
    df['visibility'] = pd.Series(visibility_list)
    df['phng_wind'] = pd.Series(wind_list)
    df['phng_wind_dir'] = pd.Series(wind_dir_list)
    df['phng_wind6hr'] = pd.Series(wind6hr_list)
    df['phng_wind12hr'] = pd.Series(wind12hr_list)
    df['phng_wind24hr'] = pd.Series(wind24hr_list)
    df['phng_wind48hr'] = pd.Series(wind48hr_list)
    df['phng_wind72hr'] = pd.Series(wind72hr_list)
    df['phng_wind120hr'] = pd.Series(wind120hr_list)
    return df


# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: add_tide_data
# Parameters: df, tide_dir
# Description: This adds NOAA CO-OPS tide data to the data frame.
# =================================================================================================
def add_tide_data(df, tide_dir):
    tideDF = pd.read_csv(tide_dir) # read in tide data
    # converting some columns to the proper data type
    tideDF['date'] = tideDF['date'].astype(str)
    tideDF['time_gmt'] = tideDF['time_gmt'].astype(str)
    tideDF['timedate'] = tideDF['date'] + ' ' + tideDF['time_gmt']
    tideDF['timedate'] = pd.to_datetime(tideDF['timedate'])
    tideDF.timedate = tideDF.timedate - dt.timedelta(hours=10) # convert from GMT to HST
    # match tide data to each sampling period in ssaData
    time_list = []
    tide_level_list = []
    for row in df.itertuples(): # going through the sample data frame
        begin_time = getattr(row, 'timedate') # getting the sample starting time
        end_time = getattr(row, 'end_time') # getting the sample ending time
        # target time is the midpoint between starting and ending time
        target_time = begin_time + (end_time - begin_time)/2
        # this finds the nearest time in the tide data to the target time
        nearest_time = min(tideDF['timedate'], key=lambda d: abs(d - target_time))
        # getting the index of that nearest time
        tide_index = tideDF.loc[tideDF['timedate'] == nearest_time].index[0]
        # appending tide information to the sample data frame
        time_list.append(tideDF.iloc[tide_index]['timedate'])
        tide_level_list.append(tideDF.iloc[tide_index]['water_level'])
    df['tide_time'] = pd.Series(time_list)
    df['tide_level'] = pd.Series(tide_level_list)
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: drop_samples
# Parameters: df, drop_list
# Description: This drops certain samples from the data frame.
# =================================================================================================
def drop_samples(df, drop_list):
    for dropID in drop_list: # for each ID in the list, the data frame excludes that sample
        df = df[df.id_number != dropID]
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: remove_low_ce
# Parameters: df
# Description: This function removes data below 40% collision efficiency. It also adds the
# collision efficiency for each bin. It recalculates into "real" concentration data the bins,
# concentration in each bin, cumulative concentration, total concentration, and salt mass.
# =================================================================================================
def remove_low_ce(df):
    # Lists are created that will eventually become columns in a data frame
    ce_list = []
    bin_conc_list = []
    total_conc_list = []
    cumu_conc_list = []
    bin_fixed_list = []
    real_salt_list = []
    total_real_salt_list = []
    for row in df.itertuples(): # walking through the sample data frame
        # these vectors are created to represent values for each bin of the size distribution
        ce_vector = [] 
        bin_conc_vector = []
        bin_fixed_vector = []
        # pulling dry radius
        bin_size_list = getattr(row, 'bin_middle')
        # pulling concentrations
        conc_list = getattr(row, 'bin_conc')
        # pulling salt
        salt_vector = getattr(row, 'bin_salt')
        # pulling pressure, convert to Pascals
        pres = getattr(row, 'pressure')
        pres = pres*100
        # pulling temperature, convert to Kelvin
        temp = getattr(row, 'temperature')
        temp = temp+273.15
        # pulling relative humidity, convert to fraction
        rh = getattr(row, 'rh')
        rh = rh/100
        # pulling wind speed
        wind = getattr(row, 'windspeed')
        # calculate collision efficiency
        ce_vector = [rw.get_collision_efficiency(pressure=pres, temperature=temp, air_speed=wind, rh=rh, dry_radius=x/1000000) for x in bin_size_list]
        # cut off data below 40% collision efficiency
        bin_conc_vector = [0 if c < 0.4 and n is not 0 else n for c,n in zip(ce_vector, conc_list)]
        # salt data cut off below 40% collision efficiency
        real_salt_vector = [0 if c < 0.4 and m is not 0 else m for c,m in zip(ce_vector, salt_vector)]
        # remove data where collision efficiency is 0
        bin_fixed_vector = [0 if c is 0 and n is not 0 else n for c,n in zip(ce_vector, conc_list)]
        # total concentration
        total_conc_list.append(sum(bin_conc_vector))
        # total salt
        total_real_salt_list.append(sum(real_salt_vector))
        # cumulative concentration
        conc_series = pd.Series(bin_conc_vector)
        cumu_conc_series = conc_series[::-1].cumsum()[::-1]
        cumu_conc_vector = cumu_conc_series.tolist()
        # append all the vectors (the distribution for each sample) to lists
        ce_list.append(ce_vector)
        bin_conc_list.append(bin_conc_vector)
        bin_fixed_list.append(bin_fixed_vector)
        cumu_conc_list.append(cumu_conc_vector)
        real_salt_list.append(real_salt_vector)
    df['bin_fixed_conc'] = bin_fixed_list
    df['bin_ce'] = ce_list
    df['bin_real_conc'] = bin_conc_list
    df['real_cumu_conc'] = cumu_conc_list
    df['real_total_conc'] = total_conc_list
    df['bin_real_salt'] = real_salt_list
    df['real_total_salt'] = total_real_salt_list
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: add_wind_sensitivity
# Parameters: df, fractional_change
# Description: This function adds hypothetical concentration data calculated by altering the wind
# by fractional_change.
# =================================================================================================
def add_wind_sensitivity(df, fractional_change):
    # defining upper and lower bounds for wind
    df['high_wind'] = df['windspeed']*(1+fractional_change)
    df['low_wind'] = df['windspeed']*(1-fractional_change)
    # This script determines the change in size distribution caused by a change in wind speed.
    # # This results from a change in wind speed changing collision efficiency and sample volume.
    highwind_ce_list = []
    lowwind_ce_list = []
    highwind_conc_list = []
    lowwind_conc_list = []
    for row in df.itertuples(): # walk through the sample data frame
        # creating vectors which is the distribution for each sample
        highwind_ce_vector = []
        lowwind_ce_vector = []
        highwind_conc_vector = []
        lowwind_conc_vector = []
        # pulling dry radius
        bin_size_list = getattr(row, 'bin_middle')
        # pulling concentrations
        conc_list = getattr(row, 'bin_conc')
        # pulling pressure, convert to Pascals
        pres = getattr(row, 'pressure')
        pres = pres*100
        # pulling temperature, convert to Kelvin
        temp = getattr(row, 'temperature')
        temp = temp+273.15
        # pulling relative humidity, convert to fraction
        rh = getattr(row, 'rh')
        rh = rh/100
        # pulling wind speed, lower bound of wind speed, upper bound of wind speed
        wind = getattr(row, 'windspeed')
        highwind = getattr(row, 'high_wind')
        lowwind = getattr(row, 'low_wind')
        # pulling collision efficiency
        ce_vector = getattr(row, 'bin_ce')
        # calculating collision efficiency for high and low wind
        # high
        highwind_ce_vector = [rw.get_collision_efficiency(pressure=pres, temperature=temp, air_speed=highwind, rh=rh, dry_radius=x/1000000) for x in bin_size_list]
        highwind_ce_list.append(highwind_ce_vector)
        # low
        lowwind_ce_vector = [rw.get_collision_efficiency(pressure=pres, temperature=temp, air_speed=lowwind, rh=rh, dry_radius=x/1000000) for x in bin_size_list]
        lowwind_ce_list.append(lowwind_ce_vector)
        # calculating concentrations for upper bound and lower bound cases of wind
        # # Concentration = Count / (Sample Volume * Collision Efficiency)
        # # # Sample Volume = Slide Width * Wind Speed * Sample Duration
        # # # Count = Concentration * Sample Volume * Collision Efficiency
        # # # Count remains the same: it represents the raw count made by the microscope software
        # # # New Concentration = Old Concentration * Old Sample Volume * Old Collision Efficiency
        # # # # divided by New Sample Volume * New Collision Efficiency
        highwind_conc_vector = [n*c1*wind/(c2*highwind) if c2 >= 0.4 else 0 for n,c1,c2 in zip(conc_list, ce_vector, highwind_ce_vector)]
        lowwind_conc_vector = [n*c1*wind/(c2*lowwind) if c2 >= 0.4 else 0 for n,c1,c2 in zip(conc_list, ce_vector, lowwind_ce_vector)]
        highwind_conc_list.append(highwind_conc_vector)
        lowwind_conc_list.append(lowwind_conc_vector)
    df['highwind_ce'] = highwind_ce_list
    df['highwind_conc'] = highwind_conc_list
    df['lowwind_ce'] = lowwind_ce_list
    df['lowwind_conc'] = lowwind_conc_list
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: add_cutoff_conc
# Parameters: df, cutoff
# Description: This function adds a cutoff to all bin concentrations so that total concentrations
# can be compared with the same cutoff. Cutoff so far is 3.9 um.
# =================================================================================================
def add_cutoff_conc(df, cutoff):
    # these lists will eventually become columns in a data frame
    bin_cutoff_conc_list = []
    bin_cutoff_salt_list = []
    cutoff_cumu_conc_list = []
    conc_cutoff_list = []
    salt_cutoff_list = []
    for row in df.itertuples(): # walks through the samples data frame
        # gccn number concentration
        concentrations = getattr(row, 'bin_real_conc')
        salts = getattr(row, 'bin_salt')
        dry_sizes = getattr(row, 'bin_lower')
        # bin concentrations with cutoff
        bin_cutoff_conc = [c if r>=cutoff else 0 for c,r in zip(concentrations, dry_sizes)]
        bin_cutoff_conc_list.append(bin_cutoff_conc)
        # bin salt with cutoff
        bin_cutoff_salt = [m if r>=cutoff else 0 for m,r in zip(salts, dry_sizes)]
        bin_cutoff_salt_list.append(bin_cutoff_salt)
        # cumulative concentrations with cutoff
        conc_series = pd.Series(bin_cutoff_conc)
        cumu_conc_series = conc_series[::-1].cumsum()[::-1]
        cumu_conc_vector = cumu_conc_series.tolist()
        cutoff_cumu_conc_list.append(cumu_conc_vector)
        # total concentrations with cutoff
        conc_cutoff = sum(c for c in concentrations if dry_sizes[concentrations.index(c)] >= cutoff)
        conc_cutoff_list.append(conc_cutoff)
        # cutoff salt mass concentration
        salt_cutoff = sum(s for s in salts if dry_sizes[salts.index(s)] >= cutoff)
        salt_cutoff_list.append(salt_cutoff)
    df['bin_cutoff_conc'] = pd.Series(bin_cutoff_conc_list)
    df['bin_cutoff_salt'] = pd.Series(bin_cutoff_salt_list)
    df['cutoff_cumu_conc'] = pd.Series(cutoff_cumu_conc_list)
    df['cutoff_total_conc'] = pd.Series(conc_cutoff_list)
    df['cutoff_total_mass'] = pd.Series(salt_cutoff_list)
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: add_low_wind_cutoff_conc
# Parameters: df, cutoff
# Description: This function does the same as add_cutoff_conc except for the hypothetical bins
# that were calculated by add_wind_sensitivity. Cutoff so far is 4.9 um
# =================================================================================================
def add_low_wind_cutoff_conc(df, cutoff):
    conc_cutoff_list = []
    for row in df.itertuples(): # walk through the sample data frame
        concentrations = getattr(row, 'lowwind_conc')
        dry_sizes = getattr(row, 'bin_lower')
        # cut off data smaller than cutoff size
        conc_cutoff = sum(c for c in concentrations if dry_sizes[concentrations.index(c)] >= cutoff)
        conc_cutoff_list.append(conc_cutoff)
    df['lowwind_total_conc'] = pd.Series(conc_cutoff_list)
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: fit_lognormal
# Parameters: df
# Description: This function tries to fit the real bin concentrations to a lognormal distribution.
# It then saves lognormal parameters to the data frame.
# =================================================================================================
def fit_lognormal(df):
    # these are the lognormal parameters that we want for each sample
    area_list = []
    muG_list = []
    sigmaG_list = []
    chi2_list = []
    p_value_list = []
    nonempty_list = []
    for row in df.itertuples(): # walk through the sample data frame
        x = getattr(row, 'bin_middle') # pull dry radius
        y = getattr(row, 'bin_cutoff_conc') # pull concentration
        w = getattr(row, 'bin_ce') # pull collision efficiency
        # we want the lognormal fit to be only for non-zero bins
        x_nonempty = [item for item,count in zip(x,y) if count>0.0]
        y_nonempty = [count for count in y if count>0.0]
        w_nonempty = [item for item,count in zip(w,y) if count>0.0]
        w_nonempty = [1/((1-item)) for item in w_nonempty]
        # change x, x_nonempty, y_nonempty, and w_nonempty to numpy arrays
        x_all = np.asarray(x)
        x_nonempty = np.asarray(x_nonempty)
        y_nonempty = np.asarray(y_nonempty)
        w_nonempty = np.asarray(w_nonempty)
        # fit the data to lognormal distribution
        model = ExpressionModel("(area)*(1/(x*sigma*sqrt(2*pi)))*exp((-(log(x)-mu)**2)/(2*(sigma**2)))")
        area_obs_fix = sum(y) # initial estimate for the area parameter
        params = model.make_params(area=area_obs_fix/0.01, sigma=0.7, mu=0)
        # set parameter minimums
        params["area"].min = 1
        params["mu"].min = math.log(0.01)
        params["mu"].max = math.log(4.5)
        params["sigma"].min = math.log(1)
        params["sigma"].max = math.log(6)
        # perform the fit
        #fit = model.fit(y_nonempty, params, x=x_nonempty)
        fit = model.fit(y_nonempty, params, x=x_nonempty, weights=w_nonempty)
        # pull fitted parameters
        area = fit.params['area'].value
        mu = fit.params['mu'].value
        sigma = fit.params['sigma'].value
        muG = math.exp(mu)
        sigmaG = math.exp(sigma)
        # calculate the fitted y-values and get chi2 and p_value
        x_lognorm, y_lognorm = x_nonempty, area*(1/(x_nonempty*sigma*math.sqrt(2*math.pi)))*np.exp((-np.power(np.log(x_nonempty)-mu, 2))/(2*np.power(sigma, 2)))
        chi2, p_value = stats.chisquare(f_obs = y_nonempty, f_exp = y_lognorm)
        chi2 = chi2/len(x_nonempty)
        # append everything to the lists
        area_list.append(area)
        muG_list.append(muG)
        sigmaG_list.append(sigmaG)
        chi2_list.append(chi2)
        p_value_list.append(p_value)
        nonempty_list.append(len(y_nonempty))
    # append the data to the data frame
    df['lognorm_area'] = pd.Series(area_list)
    df['muG'] = pd.Series(muG_list)
    df['sigmaG'] = pd.Series(sigmaG_list)
    df['chi2'] = pd.Series(chi2_list)
    df['p_value'] = pd.Series(p_value_list)
    df['dof'] = pd.Series(nonempty_list)
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: add_vocals
# Parameters: vdf, sdf
# Description: 
# =================================================================================================
def add_vocals(vdf, sdf):
    # get only the VOCALS samples between 0-650 meters altitude
    tempdf = vdf[vdf.altitude<=650]
    # get the average distribution of the selected samples
    temp_ce_list = []
    temp_conc_list = []
    for row in tempdf.itertuples():
        temp_conc = getattr(row, 'bin_real_conc')
        temp_ce = getattr(row, 'bin_ce')
        temp_size = getattr(row, 'bin_lower')
        # appending
        temp_conc_list.append(temp_conc)
        temp_ce_list.append(temp_ce)
    # convert to numpy array
    temp_conc_arrays = [np.array(item) for item in temp_conc_list]
    temp_ce_arrays = [np.array(item) for item in temp_ce_list]
    # get average
    vocals_ce = [np.mean(item) for item in zip(*temp_ce_arrays)]
    vocals_conc = [np.mean(item) for item in zip(*temp_conc_arrays)]
    # add average_ce and average_conc to ssaData
    synth_ce_list = []
    synth_conc_list = []
    for row in sdf.itertuples():
        # get sample CE and concentration and size
        sample_ce = getattr(row, 'bin_ce')
        sample_conc = getattr(row, 'bin_real_conc')
        sample_size = getattr(row, 'bin_lower')
        # replace sample data with VOCALS data if CE < 0.4
        synth_ce = [synth if item<0.4 else item for synth,item in zip(vocals_ce, sample_ce)]
        synth_conc = [synth if prob<0.4 else item for synth,prob,item in zip(vocals_conc, sample_ce, sample_conc)]
        # append to the lists
        synth_ce_list.append(synth_ce)
        synth_conc_list.append(synth_conc)
    sdf['synth_ce'] = pd.Series(synth_ce_list)
    sdf['synth_conc'] = pd.Series(synth_conc_list)
    return sdf

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: fit_synth_lognormal
# Parameters: df
# Description: This function tries to fit the synthetic bin concentrations to a lognormal 
# # distribution. It then saves lognormal parameters to the data frame.
# =================================================================================================
def fit_synth_lognormal(df):
    # these are the lognormal parameters that we want for each sample
    area_list = []
    muG_list = []
    sigmaG_list = []
    chi2_list = []
    p_value_list = []
    nonempty_list = []
    for row in df.itertuples(): # walk through the sample data frame
        x = getattr(row, 'bin_middle') # pull dry radius
        y = getattr(row, 'synth_conc') # pull concentration
        w = getattr(row, 'bin_ce') # pull collision efficiency
        # we want the lognormal fit to be only for non-zero bins
        x_nonempty = [item for item,count in zip(x,y) if count>0.0]
        y_nonempty = [count for count in y if count>0.0]
        w_nonempty = [item for item,count in zip(w,y) if count>0.0]
        w_nonempty = [1/((1-item)**2) for item in w_nonempty]
        # change x, x_nonempty, y_nonempty, and w_nonempty to numpy arrays
        x_all = np.asarray(x)
        x_nonempty = np.asarray(x_nonempty)
        y_nonempty = np.asarray(y_nonempty)
        w_nonempty = np.asarray(w_nonempty)
        # fit the data to lognormal distribution
        model = ExpressionModel("(area)*(1/(x*sigma*sqrt(2*pi)))*exp((-(log(x)-mu)**2)/(2*(sigma**2)))")
        area_obs_fix = sum(y) # initial estimate for the area parameter
        params = model.make_params(area=area_obs_fix/0.01, sigma=0.7, mu=0)
        # set parameter minimums
        params["area"].min = 0
        #params["mu"].min = math.log(0.01)
        # perform the fit
        fit = model.fit(y_nonempty, params, x=x_nonempty, weights=w_nonempty)
        # pull fitted parameters
        area = fit.params['area'].value
        mu = fit.params['mu'].value
        sigma = fit.params['sigma'].value
        muG = math.exp(mu)
        sigmaG = math.exp(sigma)
        # calculate the fitted y-values and get chi2 and p_value
        x_lognorm, y_lognorm = x_nonempty, area*(1/(x_nonempty*sigma*math.sqrt(2*math.pi)))*np.exp((-np.power(np.log(x_nonempty)-mu, 2))/(2*np.power(sigma, 2)))
        chi2, p_value = stats.chisquare(f_obs = y_nonempty, f_exp = y_lognorm)
        chi2 = chi2/len(x_nonempty)
        # append everything to the lists
        area_list.append(area)
        muG_list.append(muG)
        sigmaG_list.append(sigmaG)
        chi2_list.append(chi2)
        p_value_list.append(p_value)
        nonempty_list.append(len(y_nonempty))
    # append the data to the data frame
    df['lognorm_area'] = pd.Series(area_list)
    df['muG'] = pd.Series(muG_list)
    df['sigmaG'] = pd.Series(sigmaG_list)
    df['chi2'] = pd.Series(chi2_list)
    df['p_value'] = pd.Series(p_value_list)
    df['dof'] = pd.Series(nonempty_list)
    return df