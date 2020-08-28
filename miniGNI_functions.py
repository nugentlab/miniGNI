# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: MiniGNI Functions
# Author: Chung Taing
# Date Updated: 13 April 2020
# Description: This script provides functions for generating slide environment files. Slide
# # environment files are necessary for the GNI microscope software in analyzing the sample slides.
# # The microscope software obtains a raw count of the number of SSA on each slide. That is then
# # converted into a number concentration based on information from the slide environment file.
# =================================================================================================
# =================================================================================================
# =================================================================================================

# import packages
import datetime as dt
import math
import numpy as np
import os
import pandas as pd

# define directories
miniGNI_dir = 'C:/Users/ntril/Dropbox/mini-GNI'
flight_dir = miniGNI_dir + '/miniGNI_data'

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function: clean_GNI
# Parameters:
# # df: the mini-GNI data set
# # begin_time: the time at the start of sampling
# # time_corrector: a correction factor to account for drift in the mini-GNI's real time clock
# Description: This function sets column names for miniGNI data file. It also filters out data
# # prior to the beginning of the sampling so that you only have data from a single sampling day.
# # It also adjusts the numbers so that each variable has the following units: altitude in meters,
# # barometer temperature in degrees Celsius, pressure in Pascals, relative humidity in percent,
# # temperature in degrees Celsius, temperature in Kelvin, and alpha, beta, and gamma in radians.
# =================================================================================================
def clean_GNI(df, begin_time, time_corrector):
    # names the columns in the dataset
    df.columns = ['timedate','altitude','t_barometer','pressure','rh','temperature','door','alpha','beta','gamma']
    # adjusts each variable for the desired unit listed in description
    df.altitude/=100 # meters
    df.pressure/=100 # Pascals
    df.t_barometer/=100 # Pascals
    df.rh/=100 # fraction
    df.temperature/=100 # Celsius
    # makes all orientation angles positive
    df.beta = np.where(df.beta < 0, df.beta+360, df.beta)
    df.gamma = np.where(df.gamma < 0, df.gamma+360, df.gamma)
    # converts orientation angles to radians
    df.alpha*=(np.pi/180)
    df.beta*=(np.pi/180)
    df.gamma*=(np.pi/180)
    # removes anomalous data: humidity sensor rarely records strange spikes of >100% RH
    df = df[df.rh <= 100]
    # converts the timedate column into datetime objects
    df.timedate = [dt.datetime.strptime(date, '%Y%m%dT%H%M%S') for date in df.timedate]
    # applies the time correction factor to the timedate column
    df.timedate += time_corrector
    # removes any data from before sampling
    df = df[df.timedate > begin_time]
    # sets the timedate column as the index
    df.set_index('timedate', inplace=True)
    # creates a new column that is the temperature in Kelvin
    df['t_kelvin'] = df.temperature + 273.15
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function: clean_XQ
# Parameters:
# # df: the iMet-XQ2 dataset
# # begin_time: the time at the start of sampling
# Description: This function sets column names for the XQ dataset and removes useless columns. It
# # also filters out data prior to beginning of sampling and data in periods when the iMet-XQ2 was
# # was connected to fewer than 5 satellites. It also adjusts the variables to the correct units:
# # pressure in Pascals, temperature in Celsius and in Kelvin, relative humidity in %, humidity
# # temperature in Celsius, altitude in meters.
# =================================================================================================
def clean_XQ(df, begin_time):
    # only the columns that start with 'XQ-iMet-XQ' are needed
    df = df[df.columns[pd.Series(df.columns).str.startswith('XQ-iMet-XQ')]]
    df.columns = ['pressure', 'temperature', 'rh', 't_humidity', 'date', 'time', 'lon', 'lat', 'altitude', 'sat_count']
    df = df[df.sat_count >= 5] # removing data where connected to fewer than 5 satellites
    df['timedate'] = df.date + ' ' + df.time
    try: # there is one iMet-XQ2 instrument that records date in a different way from the others
        df.timedate = [dt.datetime.strptime(date, '%m/%d/%Y %H:%M:%S') for date in df.timedate]
    except ValueError:
        df.timedate = [dt.datetime.strptime(date, '%Y/%m/%d %H:%M:%S') for date in df.timedate]
    df.timedate = df.timedate - dt.timedelta(hours=10) # convert from UTC to HST
    df = df[df.timedate > begin_time] # filter out data prior to sampling
    df.set_index('timedate', drop=True, append=False, inplace=True) # set timedate as index
    df.drop(['date', 'time'], axis=1, inplace=True) # drop the date and time columns
    df.pressure*=100 # convert pressure to Pa
    df['t_kelvin'] = df.temperature + 273.15
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function: fix_XQ
# Parameters:
# # df: the iMet-XQ2 dataset
# Description: Occasionally, an iMet-XQ2 instrument will experience errors in recording data. This
# # functions fixes those errors.
# =================================================================================================
def fix_XQ(df):
    df.temperature/=100
    df.rh/=10
    df.t_humidity/=100
    df.lon/=10000000
    df.lat/=10000000
    df.altitude/=1000
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function: add_dewpoint_rho
# Parameters:
# # df: the mini-GNI data set
# Description: This function adds dew point temperature in degrees Celsius and air density (rho)
# # in kg/m3 to the mini-GNI dataset. It calculcates these using the temperature and pressure. This
# # also works for iMet-XQ2 datasets.
# =================================================================================================
def add_dewpoint_rho(df):
    a = np.log(df.rh/100)
    b = 17.625*df.temperature/(243.04+df.temperature) # this temperature in Celsius
    df['dew_point'] = 243*(a + b)/(17.625 - a - b)
    es = 6.113*np.exp(5423*((1/273.15) - (1/df.t_kelvin))) # this temperature in Kelvin (t_kelvin)
    e = es*df.rh/100
    df['rho'] = (0.028964*(df.pressure-(e*100)) + 0.018016*e*100)/(8.314*df.t_kelvin)
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function: correct_altitude
# Parameters
# # df: the mini-GNI data set
# # surface_pressure: the mean surface pressure given by some other instrument
# # surface_altitude: the altitude of the surface you are standing on
# Description: This function corrects the barometer's pressure given a known surface pressure
# and calculates altitude using that surface pressure and the altitude of the surface.
# The equation used to calculate altitude is h = 44330.77*(1-(p/p0)**0.1902632) + offset
# where p is the pressure, p0 is the surface pressure, and offset is the surface altitude
# =================================================================================================
def correct_altitude(df, surface_pressure, surface_altitude):
    # calculating the difference between altitudes at each data point in the time series
    df['altdiff'] = df.altitude.diff()
    df.iloc[0, df.columns.get_loc('altdiff')] = 0
    # defining a cut off altimeter altitude so that we can calculate surface pressure
    cutoffAlt = df.altitude.min() + 10
    # calculating mean surface pressure at altitude below the cutoff altitude
    gni_surface_pressure = df[(df['altdiff'] < 1) & (df['altitude'] < cutoffAlt)].pressure.mean()
    # getting the difference between the known surface pressure and the gni's measured surface pressure
    pressure_diff = surface_pressure - gni_surface_pressure
    # correcting the pressure by that pressure difference
    df['pressure'] += pressure_diff
    df.drop('altdiff', axis=1, inplace=True)
    # recalculates altitude using mean surface pressure, taking into account ground elevation
    df['altitude'] = 44330.77*(1-(df.pressure/surface_pressure)**0.1902632) + surface_altitude
    return df

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function: retrieve_samples
# Parameters
# # df: the mini-GNI data set
# Description: This function detects the sampling periods by finding where the door was open.
# Additionally, it separates the different sampling times and returns a list of data frames where
# each data frame is the data frame for the duration of a sampling period.
# =================================================================================================
def retrieve_samples(df):
    # reduces the data to where the door was open
    samples = df[(gnidf.door == 1)]
    samples['myIndex'] = range(1, len(samples)+1)
    # finds the time difference between each data point
    samples['tdiff'] = samples.index.to_series().diff().dt.seconds
    samples.ix[0, 'tdiff'] = 0.0
    # When the time difference between 2 points is very great, that means those 2 points represent
    # # the end of one sample and the start of another. The function splits the data frame there.
    # # THe time difference threshold is arbitrary: it is five minutes here because more than five
    # # minutes pass between each sample period.
    indxList = samples.myIndex[samples['tdiff'] > 300]
    indxList = pd.concat([pd.Series([1]), indxList, pd.Series([len(samples)])], ignore_index=True)
    sample_list = [samples[(samples.myIndex >= indxList[i]) & (samples.myIndex < indxList[i+1])] for i in range(len(indxList)-1)]
    return sample_list

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function: retrieve_xqSample
# Parameters
# # xqdf: the iMet-XQ2 data set
# # gnidf: the mini-GNI data set
# Description: This function returns the part of the iMet-XQ2 data frame that matches up to the
# # time of the mini-GNI data frame.
# =================================================================================================
def retrieve_xqSample(xqdf, gnidf):
    t1 = gnidf.index[0]
    t2 = gnidf.index[-1]
    sampleXQ = xqdf[(xqdf.index >= t1) & (xqdf.index <= t2)]
    return sampleXQ

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function: rename_environment_files
# Parameters:
# # sample_year: the year when the samples were taken
# # sample_month: the month when the samples were taken
# # sample_day: the day when the samples were taken
# Description: This function renames all the slide environment files in a folder and also corrects
# # the slide number in each file. Recall that the slide environment files are required by the
# # GNI microscope software to calculate number concentration.
# =================================================================================================
def rename_environment_files(sample_year, sample_month, sample_day):
    date_label = sample_year[2:] + sample_month + sample_day
    environment_dir = flight_dir + '/' + sample_year + '_' + sample_month + '_' + sample_day + '/slides'
    # slide number counter
    counter = 1
    for subdir, dirs, files in os.walk(environment_dir):
        for file in files:
            if file.startswith(date_label + 'gni'):
                filepath = environment_dir + '/' + file
                new_filepath = environment_dir + '/' + 'sli_env_' + date_label + 'a' + str(counter)
                myfile = open(filepath, 'r')
                filelines = myfile.readlines()
                myfile.close()
                if counter < 10:
                    filelines[3] = '            {}.    slide_number \n'.format(counter)
                else:
                    filelines[3] = '           {}.    slide_number \n'.format(counter)
                new_file = open(new_filepath, 'w')
                new_file.writelines(filelines)
                new_file.close()
                counter += 1

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function: generate_environment_files
# Parameters:
# # gni_number: the mini-GNI instrument number that took the samples as a string
# # sample_year: the year when the samples were taken as a string
# # sample_month: the month when the samples were taken as a string
# # sample_day: the day when the samples were taken as a string
# # sample_hour: the hour when the samples started being taken as a string
# # sample_minute: the minutes when the samples started being taken as a string
# # windspeed_bar: a list of average surface wind speed (float format) for each sample taken
# # windspeed_min: same as previous except the minimum wind speeds
# # windspeed_max: same as previous except the maximum wind speeds
# # wind_dir: the average wind direction of the sampling day (float format)
# # surface_height: the height where surface wind speed measurements are taken (float format)
# # lon: the longitude of the sampling location (float format)
# # lat: the latitude of the sampling location (float format)
# # time_corrector: the correction factor for the mini-GNI instrument because its real time clock
# # # tends to drift over time (datetime timedelta object)
# Description: This function generates slide environment files for all samples taken with a
# # specific mini-GNI instrument on a particular sample date.
# =================================================================================================
def generate_environment_files(gni_number, sample_year, sample_month, sample_day, sample_hour, sample_minute, windspeed_bar, windspeed_min, windspeed_max, wind_dir, surface_height, lon, lat, time_corrector=dt.timedelta(0)):
    # create a date label of the sample date
    date_label = sample_year[2:] + sample_month + sample_day
    # define the directory where we will pull mini-GNI and iMet-XQ2 data from for the sample day
    sample_dir = flight_dir + '/' + sample_year + '_' + sample_month + '_' + sample_day
    # convert the time string variables defined above into a datetime
    sample_time = dt.datetime.strptime(sample_year + sample_month + sample_day + sample_hour + sample_minute + '00', '%Y%m%d%H%M%S')
    # retrieve miniGNI data corresponding to the correct mini-GNI number
    gni_dir = sample_dir + '/data/' + date_label + '_gni' + gni_number + '.csv'
    gniDF = pd.read_csv(gni_dir, header=None)
    gniDF = clean_GNI(gniDF, begin_time=sample_time, time_corrector=time_corrector)
    # This walks through the sample_dir directory to search for surface_XQ data. This iMet-XQ2
    # # data set is only necessary for when the mini-GNI does not have a humidity sensor.
    for subdir, dirs, files in os.walk(sample_dir + '/data'):
        for file in files:
            if file.startswith(dateLabel + '_surface_xq'):
                surfaceXQ = pd.read_csv(sample_dir + '/data/' + file)
                surfaceXQ = clean_XQ(surfaceXQ, begin_time=sample_time)
                surfaceXQ = add_dewpoint_rho(surfaceXQ)
    # add dew point and air density data if the mini-GNI has a humidity sensor
    gni_has_RH = bool(gniDF['rh'].mean() > 0) # checks if the RH data exists
    if gni_has_RH:
        gniDF = add_dewpoint_rho(gniDF)
    # calibrate the mini-GNI pressure to mean surface pressure read by then surface iMet-XQ2
    # # and also recalculate the altitude from the calibrated pressure
    xq_surface_pressure = surfaceXQ['pressure'].mean()
    gniDF = correct_altitude(gniDF, surface_pressure=xq_surface_pressure, surface_altitude=surface_height)
    # obtain a list of data frames, one data frame for each sampling period
    all_samples = retrieve_samples(gniDF)
    # This generates slide environment files for each sample period. If windspeed_bar contains
    # # a -1 value, then that sample period is considered invalid, and the environment file
    # # is not generated for that sample. e.g. if windspeed_bar = [4.5, -1, 3.0], then the second
    # # data frame in all_samples is not analyzed for sampling data.
    # What this does is pull relevant data from the mini-GNI sampling period data set and then
    # # puts them all into strings. These strings will all become lines in a text file.
    for i in range(len(windspeed_bar)):
        if windspeed_bar[i] > 0:
            # pulls the ith sampling data from the list of data frames
            gni_sample = all_samples[i]
            # creates the year month day string
            yymmdd_str = '       {}.    yymmdd'.format(date_label)
            # get the beginning and end of the sampling period
            hhmmss_begin = gni_sample.index[0].strftime('%H%M%S')
            hhmmss_end = gni_sample.index[-1].strftime('%H%M%S')
            # creates strings marking the begining and ending time of the sampling period
            hhmmss_begin_str = '      {}.0    hhmmss_begin'.format(hhmmss_begin)
            hhmmss_end_str = '      {}.0    hhmmss_end'.format(hhmmss_end)
            # This creates the slide number string. Note that the function rename_environment_files
            # # edits these lines later as they will be incorrect right now since we are generating
            # # environment files for each mini-GNI instrument individually whereas the slide
            # # number depends on how many instruments were used and how many samples were taken
            # # per instrument.
            slide_number_str = '            {}.    slide_number'.format(i+1)
            # field project number string, which defaults to 0 and doesn't need to be worried about
            project_str = '            0.    field_project'
            # =====================================================================================
            # This calculates the wind speed average, min, and max aloft. It uses the power law
            # # to convert average, min, and max surface wind to aloft wind. The power law is
            # # u = u_surface * (z / z_surface)^0.143. This also rounds each to the nearest
            # # hundredths place.
            wind_aloft_bar = windspeed_bar[i]*((gni_sample['altitude'].mean())/surface_height)**0.143
            wind_aloft_bar = round(wind_aloft_bar, 2)
            wind_aloft_min = windspeed_min[i]*((gni_sample['altitude'].mean())/surface_height)**0.143
            wind_aloft_min = round(wind_aloft_min, 2)
            wind_aloft_max = windspeed_max[i]*((gni_sample['altitude'].mean())/surface_height)**0.143
            wind_aloft_max = round(wind_aloft_max, 2)
            # This creates the strings for wind speed aloft average, min, and max. Note that it
            # # creates both tas string and windspeed string. This is because the mini-GNI sampling
            # # was done on a kite platform rather than a moving platform (such as an aircraft,
            # # drone, or UAS). Thus, the air speed and the wind speed are the same. Note that the
            # # string lengths change based on the value of the wind speed due to the number of
            # # digits. This does not account for wind speed over 99.99 m/s because this is not
            # # possible for the kite platform to observe. If this method were to be adapted for
            # # a moving platform, this section of the code would have to be changed.
            # wind average
            if wind_aloft_bar < 10:
                tas_bar_str = '          {:.2f}    tas_bar'.format(wind_aloft_bar)
                windspeed_bar_str = '          {:.2f}    wind_speed_bar'.format(wind_aloft_bar)
            else:
                tas_bar_str = '         {:.2f}    tas_bar'.format(wind_aloft_bar)
                windspeed_bar_str = '         {:.2f}    wind_speed_bar'.format(wind_aloft_bar)
            # wind minimum
            if wind_aloft_min < 10:
                tas_min_str = '          {:.2f}    tas_min'.format(wind_aloft_min)
                windspeed_min_str = '          {:.2f}    wind_speed_min'.format(wind_aloft_min)
            else:
                tas_min_str = '         {:.2f}    tas_min'.format(wind_aloft_min)
                windspeed_min_str = '         {:.2f}    wind_speed_min'.format(wind_aloft_min)
            # wind maximum
            if wind_aloft_max < 10:
                tas_max_str = '          {:.2f}    tas_max'.format(wind_aloft_max)
                windspeed_max_str = '          {:.2f}    wind_speed_max'.format(wind_aloft_max)
            else:
                tas_max_str = '         {:.2f}    tas_max'.format(wind_aloft_max)
                windspeed_max_str = '         {:.2f}    wind_speed_max'.format(wind_aloft_max)
            # =====================================================================================
            # Check if miniGNI has humidity data. If not, then the iMet-XQ2 data surfaceXQ will
            # # be used to help calculate relative humidity, dew point, and air density aloft.
            # # Average, min, and max values are required for each variable.
            if gni_has_RH: # then the data can be pulled directly from the mini-GNI
                # relative humidity
                rh_bar = round(gni_sample['rh'].mean()/100, 4)
                rh_min = round(gni_sample['rh'].min()/100, 4)
                rh_max = round(gni_sample['rh'].max()/100, 4)
                # air density
                rho_bar = round(gni_sample['rho'].mean(), 3)
                rho_min = round(gni_sample['rho'].min(), 3)
                rho_max = round(gni_sample['rho'].max(), 3)
                # dew point temperature
                td_bar = round(gni_sample['dew_point'].mean() + 273.15, 2)
                td_min = round(gni_sample['dew_point'].min() + 273.15, 2)
                td_max = round(gni_sample['dew_point'].max() + 273.15, 2)
            else:
                # retreive XQ data for corresponding sampling period
                xqSample = retrieve_xqSample(xqdf=surfaceXQ, gnidf=gni_sample)
                # get XQ surface data for temperature and relative humidity
                xq_temp_bar = xqSample['t_kelvin'].mean()
                xq_rh_bar = xqSample['rh'].mean()
                xq_rh_min = xqSample['rh'].min()
                xq_rh_max = xqSample['rh'].max()
                # calculate average saturation vapor pressure at surface
                xq_sat_vapor = 6.113*math.exp(5423*((1/273.15) - (1/xq_temp_bar)))
                # calculate vapor pressure average, minimum, maximum at surface
                vapor_bar = xq_sat_vapor*(xq_rh_bar/100)
                vapor_min = xq_sat_vapor*(xq_rh_min/100)
                vapor_max = xq_sat_vapor*(xq_rh_max/100)
                # get miniGNI temperature aloft
                gni_temp_bar = gni_sample['t_kelvin'].mean()
                gni_temp_min = gni_sample['t_kelvin'].min()
                gni_temp_max = gni_sample['t_kelvin'].max()
                # calculate average saturation vapor pressure at miniGNI aloft
                gni_sat_vapor = 6.113*math.exp(5423*((1/273.15) - (1/gni_temp_bar)))
                # This now calculate the variables at the miniGNI aloft. It is assumed that the
                # # atmosphere up to the height of the mini-GNI is well mixed so that the vapor
                # # pressure is the same at the surface and at aloft.
                # relative humidity (in fraction form)
                rh_bar = vapor_bar/gni_sat_vapor
                rh_min = vapor_min/gni_sat_vapor
                rh_max = vapor_max/gni_sat_vapor
                # gets temperature for dew point calculation
                # # (the calculation uses Celsius, so need to convert)
                gni_temp_bar -= 273.15
                gni_temp_min -= 273.15
                gni_temp_max -= 273.15
                # dew point calculation
                td_bar = 243.04*(math.log(rh_bar)+((17.625*gni_temp_bar)/(243.04+gni_temp_bar)))/(17.625-math.log(rh_bar)-((17.625*gni_temp_bar)/(243.04+gni_temp_bar)))
                td_min = 243.04*(math.log(rh_bar)+((17.625*gni_temp_min)/(243.04+gni_temp_min)))/(17.625-math.log(rh_bar)-((17.625*gni_temp_min)/(243.04+gni_temp_min)))
                td_max = 243.04*(math.log(rh_bar)+((17.625*gni_temp_max)/(243.04+gni_temp_max)))/(17.625-math.log(rh_bar)-((17.625*gni_temp_max)/(243.04+gni_temp_max)))
                # convert variables back to form required in sli_env file
                # # temperatures in Kelvin
                td_bar += 273.15
                td_min += 273.15
                td_max += 273.15
                gni_temp_bar += 273.15
                gni_temp_min += 273.15
                gni_temp_max += 273.15
                # calculate air density aloft
                # # uses miniGNI air pressure, vapor pressure, temperature in Kelvin
                gni_pres_bar = gni_sample['pressure'].mean()
                rho_bar = (0.028964*(gni_pres_bar - 100*vapor_bar) + 0.018016*100*vapor_bar)/(8.314*gni_temp_bar)
                rho_min = (0.028964*(gni_pres_bar - 100*vapor_max) + 0.018016*100*vapor_max)/(8.314*gni_temp_bar)
                rho_max = (0.028964*(gni_pres_bar - 100*vapor_min) + 0.018016*100*vapor_min)/(8.314*gni_temp_bar)
                # round all variables so we can generate string lines
                rh_bar = round(rh_bar, 4)
                rh_min = round(rh_min, 4)
                rh_max = round(rh_max, 4)
                td_bar = round(td_bar, 2)
                td_min = round(td_min, 2)
                td_max = round(td_max, 2)
                rho_bar = round(rho_bar, 3)
                rho_min = round(rho_min, 3)
                rho_max = round(rho_max, 3)
            # creates string lines for relative humidity
            rh_bar_str = '        {:.4f}    rel_hum_bar'.format(rh_bar)
            rh_min_str = '        {:.4f}    rel_hum_min'.format(rh_min)
            rh_max_str = '        {:.4f}    rel_hum_max'.format(rh_max)
            # creats string lines for air density
            rho_bar_str = '         {:.3f}    rho_air_bar'.format(rho_bar)
            rho_min_str = '         {:.3f}    rho_air_min'.format(rho_min)
            rho_max_str = '         {:.3f}    rho_air_max'.format(rho_max)
            # get the mini-GNI temperature data
            temp_bar = round(gni_sample['t_kelvin'].mean(), 2)
            temp_min = round(gni_sample['t_kelvin'].min(), 2)
            temp_max = round(gni_sample['t_kelvin'].max(), 2)
            # creates string lines for temperature
            temp_bar_str = '        {:.2f}    t_bar'.format(temp_bar)
            temp_min_str = '        {:.2f}    t_min'.format(temp_min)
            temp_max_str = '        {:.2f}    t_max'.format(temp_max)
            # create string lines for dew point temperature
            td_bar_str = '        {:.2f}    td_bar'.format(td_bar)
            td_min_str = '        {:.2f}    td_min'.format(td_min)
            td_max_str = '        {:.2f}    td_max'.format(td_max)
            # =====================================================================================
            # get the mini-GNI pressure data
            pres_bar = int(gni_sample['pressure'].mean())
            pres_min = int(gni_sample['pressure'].min())
            pres_max = int(gni_sample['pressure'].max())
            # This create string lines for pressure. Note that the number of digits for pressure
            # # can change, so the string length changes.
            # pressure average
            if pres_bar < 100000:
                pres_bar_str = '        {}.    p_bar'.format(pres_bar)
            else:
                pres_bar_str = '       {}.    p_bar'.format(pres_bar)
            # pressure minimum
            if pres_min < 100000:
                pres_min_str = '        {}.    p_min'.format(pres_min)
            else:
                pres_min_str = '       {}.    p_min'.format(pres_min)
            # pressure maximum
            if pres_max < 100000:
                pres_max_str = '        {}.    p_max'.format(pres_max)
            else:
                pres_max_str = '       {}.    p_max'.format(pres_max)
            # =====================================================================================
            # get the mini-GNI altitude data
            z_bar = int(gni_sample['altitude'].mean())
            z_min = int(gni_sample['altitude'].min())
            z_max = int(gni_sample['altitude'].max())
            z_begin = int(gni_sample['altitude'].iloc[0])
            z_end = int(gni_sample['altitude'].iloc[-1])
            # This creates string lines for altitude. Note that the number of digits for altitude
            # # can change, so the string length changes. Currently, this section accounts for
            # # altitudes from 1-9999 meters.
            # altitude average
            if z_bar >= 1000:
                z_bar_str = '         {}.    z_bar'.format(z_bar)
            elif z_bar >= 100:
                z_bar_str = '          {}.    z_bar'.format(z_bar)
            elif z_bar >= 10:
                z_bar_str = '           {}.    z_bar'.format(z_bar)
            else:
                z_bar_str = '            {}.    z_bar'.format(z_bar)
            # altitude minimum
            if z_min >= 1000:
                z_min_str = '         {}.    z_min'.format(z_min)
            elif z_min >= 100:
                z_min_str = '          {}.    z_min'.format(z_min)
            elif z_min >= 10:
                z_min_str = '           {}.    z_min'.format(z_min)
            else:
                z_min_str = '            {}.    z_min'.format(z_min)
            # altitude maximum
            if z_max >= 1000:
                z_max_str = '         {}.    z_max'.format(z_max)
            elif z_max >= 100:
                z_max_str = '          {}.    z_max'.format(z_max)
            elif z_max >= 10:
                z_max_str = '           {}.    z_max'.format(z_max)
            else:
                z_max_str = '            {}.    z_max'.format(z_max)
            # altitude at beginning of sample period
            if z_begin >= 1000:
                z_begin_str = '         {}.    z_begin'.format(z_begin)
            elif z_begin >= 100:
                z_begin_str = '          {}.    z_begin'.format(z_begin)
            elif z_begin >= 10:
                z_begin_str = '           {}.    z_begin'.format(z_begin)
            else:
                z_begin_str = '            {}.    z_begin'.format(z_begin)
            # altitude at end of sampling period
            if z_end >= 1000:
                z_end_str = '         {}.    z_end'.format(z_end)
            elif z_end >= 100:
                z_end_str = '          {}.    z_end'.format(z_end)
            elif z_end >= 10:
                z_end_str = '           {}.    z_end'.format(z_end)
            else:
                z_end_str = '            {}.    z_end'.format(z_end)
            # =====================================================================================
            # This creates the wind direction string. Note that the number of digits in wind
            # # direction changes as the value changes. The string length therefore needs to be
            # # varied. This accounts for all wind directions from 0-360 degrees.
            if wind_dir >= 100:
                wind_dir_str = '        {:.2f}    wind_direction_bar'.format(wind_dir)
            elif wind_dir >= 10:
                wind_dir_str = '         {:.2f}    wind_direction_bar'.format(wind_dir)
            else:
                wind_dir_str = '          {:.2f}    wind_direction_bar'.format(wind_dir)
            # =====================================================================================
            # This creates the longitude and latitude strings. Note that the average longitude
            # # and latitude is currently being used for all of the average, minimum, and maximum
            # # longitude and latitude strings. This accounts for all longitudes from -180 to 180
            # # degrees and all latitudes from -90 to 90 degrees.
            # longitude
            if lon >= 100:
                lon_bar_str = '        {:.2f}    longitude_bar'.format(lon)
                lon_min_str = '        {:.2f}    longitude_min'.format(lon)
                lon_max_str = '        {:.2f}    longitude_max'.format(lon)
            elif lon >= 10:
                lon_bar_str = '         {:.2f}    longitude_bar'.format(lon)
                lon_min_str = '         {:.2f}    longitude_min'.format(lon)
                lon_max_str = '         {:.2f}    longitude_max'.format(lon)
            elif lon >= 0:
                lon_bar_str = '          {:.2f}    longitude_bar'.format(lon)
                lon_min_str = '          {:.2f}    longitude_min'.format(lon)
                lon_max_str = '          {:.2f}    longitude_max'.format(lon)
            elif lon > -10:
                lon_bar_str = '         {:+.2f}    longitude_bar'.format(lon)
                lon_min_str = '         {:+.2f}    longitude_min'.format(lon)
                lon_max_str = '         {:+.2f}    longitude_max'.format(lon)
            elif lon > -100:
                lon_bar_str = '        {:+.2f}    longitude_bar'.format(lon)
                lon_min_str = '        {:+.2f}    longitude_min'.format(lon)
                lon_max_str = '        {:+.2f}    longitude_max'.format(lon)
            else:
                lon_bar_str = '       {:+.2f}    longitude_bar'.format(lon)
                lon_min_str = '       {:+.2f}    longitude_min'.format(lon)
                lon_max_str = '       {:+.2f}    longitude_max'.format(lon)
            # latitude
            if lat >= 10:
                lat_bar_str = '         {:.2f}    latitude_bar'.format(lat)
                lat_min_str = '         {:.2f}    latitude_min'.format(lat)
                lat_max_str = '         {:.2f}    latitude_max'.format(lat)
            elif lat >= 0:
                lat_bar_str = '          {:.2f}    latitude_bar'.format(lat)
                lat_min_str = '          {:.2f}    latitude_min'.format(lat)
                lat_max_str = '          {:.2f}    latitude_max'.format(lat)
            elif lat > -10:
                lat_bar_str = '         {:+.2f}    latitude_bar'.format(lat)
                lat_min_str = '         {:+.2f}    latitude_min'.format(lat)
                lat_max_str = '         {:+.2f}    latitude_max'.format(lat)
            else:
                lat_bar_str = '        {:+.2f}    latitude_bar'.format(lat)
                lat_min_str = '        {:+.2f}    latitude_min'.format(lat)
                lat_max_str = '        {:+.2f}    latitude_max'.format(lat)
            # =====================================================================================
            # Now, all the strings created can be written to an environment file. First, the file
            # # name is generated using the date_label and the mini-GNI number. The naming system
            # # used here is essential for the function rename_environment_files to work. The
            # # reason that the files have to later be renamed is that this function only generates
            # # environment files for one particular mini-GNI, defined by gni_number. The files
            # # to be named taking into account the number of mini-GNIs used, so they have to be
            # # renamed at a later time. The naming system used here results in the text files
            # # being ordered in the directory like so (with X being used to substitude date
            # # values): X_gni1s1, X_gni1s2, X_gni1s3, X_gni2s1, X_gni2s2, etc. This later allows
            # # them to be renamed in order to Xa1, Xa2, Xa3, Xa4, Xa5, etc.
            environment_file_name = sample_dir + '/slides/' + date_label + 'gni' + gni_number + 's' + str(i+1) + '.txt'
            # putting all the strings into lines of a text file in a specific order
            environment_file_lines = [yymmdd_str, hhmmss_begin_str, hhmmss_end_str, slide_number_str, project_str, tas_bar_str, tas_min_str, tas_max_str, rh_bar_str, rh_min_str, rh_max_str, rho_bar_str, rho_min_str, rho_max_str, temp_bar_str, temp_min_str, temp_max_str, td_bar_str, td_min_str, td_max_str, pres_bar_str, pres_min_str, pres_max_str, z_bar_str, z_min_str, z_max_str, z_begin_str, z_end_str, windspeed_bar_str, windspeed_min_str, windspeed_max_str, wind_dir_str, lon_bar_str, lon_min_str, lon_max_str, lat_bar_str, lat_min_str, lat_max_str]
            environment_file_lines = [s + ' \n' for s in environment_file_lines]
            f = open(environment_file_name, 'w')
            f.writelines(environment_file_lines)
            f.close()
