# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: Anemometer Plotter
# Author: Chung Taing
# Date Updated: 11 April 2020
# Description: This script provides reads and plots anemometer data. The data is a vertical wind
# # profile. It then fits the data to a wind profile log law and compares that to a theoretical
# # wind profile power law.
# =================================================================================================
# =================================================================================================
# =================================================================================================

# importing packages and functions
import datetime as dt
import math
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import os

from matplotlib.dates import DateFormatter

import miniGNI_functions as mgf

plt.close('all') # close any residual plots

# define directories
miniGNI_dir = 'C:/Users/ntril/Dropbox/mini-GNI'
flight_dir = miniGNI_dir + '/miniGNI_data'

# =================================================================================================
# IMPORTANT VALUES DEFINED HERE ===================================================================
# =================================================================================================

# Define here as strings the year, month and day of the sample. Also define the hour and minute
# # just before the sampling began. This allows for filtering out of old data.
sample_year = '2019' # 4 digit year, must be string
sample_month = '10' # 2 digit month, must be string
sample_day = '03' # 2 digit day, must be string
sample_hour = '11' # 2 digit hour from 0-24, no AM/PM, must be string
sample_minute = '30' # 2 digit minute, must be string
# creates a date label of the sampling date
date_label = sample_year[2:] + sample_month + sample_day
# defines the directory of the sampling date
sample_dir = flightBaseDir + '/' + sample_year + '_' + sample_month + '_' + sample_day
plot_dir = sample_dir + '_wind/plots'
data_dir = sample_dir + '_wind/data'
# creates date label for the plots
plt_date_label = sample_month + '/' + sample_day + '/' + sample_year
# turns the defined date strings into a datetime
sample_time = dt.datetime.strptime(sample_year + sample_month + sample_day + sample_hour + sample_minute + '00', '%Y%m%d%H%M%S')

# define here which XQ was at surface and which was aloft
surface_XQ_num = '9'
aloft_XQ_num = '7'

# This defines a time correction factor because the mini-GNI real time clock drifts.
# Unfortunately, the time correction factor needs to be found manually by matching up pressure
# # time series of the anemometer to the iMet-XQ2 aloft. The correction factors should be set to
# # zero as default if it has not been found yet.
# the time correction factors found for 10/3/19 sampling day:
time_corrector_a1 = dt.timedelta(seconds=-1)
time_corrector_a2 = dt.timedelta(seconds=-384)

# =================================================================================================
# =================================================================================================
# =================================================================================================
# THIS SECTION DEFINES FUNCTIONS ==================================================================
# =================================================================================================
# =================================================================================================
# =================================================================================================

# =================================================================================================
# Function: clean_anemometer
# Parameters:
# # df: the custom anemometer data set
# # begin_time: the time when you started sampling
# # time_corrector: a correction factor to manually account for drift in the RTC add-on
# Description: This function corrects the numbers so that each variable has the following units:
# # altitude in meters, barometer temperature in degrees Celsius, pressure in Pascals, temperature
# # in degrees Celsius, and temperature in Kelvin. It also filters out data prior to the beginning
# # of the sampling so that you only have data from a single sampling day.
# =================================================================================================
def clean_anemometer(df, begin_time, time_corrector):
    # fixing units and adding temperature in Kelvin
    df.altitude/=100
    df.pressure/=100
    df.temperature/=100
    df['t_kelvin'] = df.temperature + 273.15
    # converting timedate column to datetime object
    df.timedate = [dt.datetime.strptime(date, '%m/%d/%YT%H:%M:%S') for date in df.timedate]
    # corrects the time
    df.timedate += time_corrector
    # filters out data from previous days
    df = df[df.timedate > begin_time]
    df.set_index('timedate', inplace=True)
    return df

# This function retrieves a sample data frame defined by the starting and ending time of the
# # sample from the anemometer data frame.
def retrieve_sample(df, start_time, end_time):
    sample_start = dt.datetime.strptime(date_label + start_time, '%y%m%d%H%M%S')
    sample_end = dt.datetime.strptime(date_label + end_time, '%y%m%d%H%M%S')
    dfSample = df[(df.index >= sample_start) & (df.index <= sample_end)]
    return dfSample

# This function retrieves all the samples, defined manually, and outputs a list of data frames
# # where each data frame is one sample.
def get_all_samples(df):
    df1 = retrieve_sample(df=df, start_time='120400', end_time='121200')
    df2 = retrieve_sample(df=df, start_time='122300', end_time='123100')
    df3 = retrieve_sample(df=df, start_time='123600', end_time='124400')
    df4 = retrieve_sample(df=df, start_time='124800', end_time='125600')
    df5 = retrieve_sample(df=df, start_time='130100', end_time='130900')
    df6 = retrieve_sample(df=df, start_time='131400', end_time='132200')
    df7 = retrieve_sample(df=df, start_time='132700', end_time='133500')
    df8 = retrieve_sample(df=df, start_time='133900', end_time='134700')
    df9 = retrieve_sample(df=df, start_time='135200', end_time='140000')
    df10 = retrieve_sample(df=df, start_time='140500', end_time='141300')
    df11 = retrieve_sample(df=df, start_time='141900', end_time='142700')
    df12 = retrieve_sample(df=df, start_time='143200', end_time='144000')
    df13 = retrieve_sample(df=df, start_time='144700', end_time='145500')
    df14 = retrieve_sample(df=df, start_time='150200', end_time='151000')
    df15 = retrieve_sample(df=df, start_time='151700', end_time='152500')
    df16 = retrieve_sample(df=df, start_time='153000', end_time='153800')
    df17 = retrieve_sample(df=df, start_time='154600', end_time='155400')
    samples_list = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df13, df14, df15, df16, df17])
    return samples_list

# This function retrieves all the samples, defined manually, and outputs the average altitude and
# # wind speed of each sample.
def get_sample_averages(df):
    samples_list = get_all_samples(df)
    mean_alt_list = []
    mean_wind_list = []
    [mean_alt_list.append(x.altitude.mean()) for x in samples_list]
    [mean_wind_list.append(x.windspeed.mean()) for x in samples_list]
    meanDF = pd.DataFrame()
    meanDF['altitude'] = pd.Series(mean_alt_list)
    meanDF['windspeed'] = pd.Series(mean_wind_list)
    return meanDF

# =================================================================================================
# =================================================================================================
# =================================================================================================

# read in anemometer data
anem1 = pd.read_csv(data_dir + '/' + date_label + '_anem1.csv')
anem2 = pd.read_csv(data_dir + '/' + date_label + '_anem2.csv')

# read in iMet-XQ2 data
surfaceXQ = pd.read_csv(data_dir + '/' + date_label + '_surface_xq' + surface_XQ_num + '.csv')
aloftXQ = pd.read_csv(data_dir + '/' + date_label + '_aloft_xq' + aloft_XQ_num + '.csv')

# cleaning the anemometer data
anem1 = clean_anemometer(anem1, begin_time=sample_time, time_corrector=time_corrector_a1)
anem2 = clean_anemometer(anem2, begin_time=sample_time, time_corrector=time_corrector_a2)
# This excludes all data where wind speed is less than 0.5 m/s because there were times at the
# # surface when the anemometers were lying on the ground reading 0. This is okay because the
# # sampling day had strong trade wind conditions.
anem1 = anem1[anem1.windspeed > 0.5]
anem2 = anem2[anem2.windspeed > 0.5]

# cleaning iMet-XQ2 data
aloftXQ = mgf.clean_XQ(aloftXQ, begin_time=sample_time)
surfaceXQ = mgf.clean_XQ(surfaceXQ, begin_time=sample_time)

# correcting altitude
mean_surface_pressure = surfaceXQ['pressure'].mean()
anem1 = mgf.correctAltitude(anem1, surface_pressure=mean_surface_pressure, surface_altitude=8)
anem2 = mgf.correctAltitude(anem2, surface_pressure=mean_surface_pressure, surface_altitude=0)

# retrieve all the samples
anem1_samples = get_all_samples(df=anem1)
anem2_samples = get_all_samples(df=anem2)
anem_samples = pd.concat([anem1_samples, anem2_samples])

# retreive the mean of each sample
anem1_mean = get_sample_averages(df=anem1)
anem2_mean = get_sample_averages(df=anem2)
anem_mean = pd.concat([anem1_mean, anem2_mean])

# =================================================================================================
# POWER LAW AND LOG LAW ===========================================================================
# =================================================================================================

res = 100 # resolution of fitted data
mean_surface_wind = 5.4 # the mean surface wind speed of the sampling day

alt_list = [z/res for z in range(50, 600*res+1)]
power_list = [mean_surface_wind*(z/2.5)**0.143 for z in alt_list]
logList = [mean_surface_wind*(math.log(z/0.1564)/math.log(24.48555/0.1564)) for z in alt_list]

# fitting all points to data
y1 = anem_samples.altitude
x1 = anem_samples.windspeed
z1 = np.polyfit(np.log(y1), x1, 1, full=True)
# print(z1) outputs [1.06209833, 2.02767197] as coefficients with residuals = 3908.49972412
fitted_list = [(1.06209833*math.log(z) + 2.02767197) for z in alt_list]

# =================================================================================================
# PLOT FUNCTIONS ==================================================================================
# =================================================================================================

# This function prints the time of minimum pressure for the two anemometers and the iMet-XQ2
# # instrument aloft prior to some cutoff time. This allows you to try to manually match up the
# # data sets to account for the drift in the anemometer real time clock.
def print_time_of_min_pressure(time_cutoff):
    someTime = dt.datetime.strptime(date_label + time_cutoff, '%y%m%d%H%M%S')
    print(anem1[anem1.index < someTime].pressure.idxmin(axis=0))
    print(anem2[anem2.index < someTime].pressure.idxmin(axis=0))
    print(aloftXQ[aloftXQ.index < someTime].pressure.idxmin(axis=0))

# This function plots the pressure time series of the anemometers and the iMet-XQ2 instruments.
# # This does not save the plot. It only shows the plot. This function can help assist in
# # lining up the anemometer and iMet-XQ2 data sets to account for the anemometer real time
# # clock drift.
def plot_pressure():
    myFmt = DateFormatter('%H:%M') # time format
    plt.rcParams['figure.figsize'] = (8.0, 6.0) # figure size
    fig, ax = plt.subplots()
    surfaceXQ.pressure.plot(label = 'XQ Surface', color='grey')
    aloftXQ.pressure.plot(label='XQ Aloft', color='black')
    anem1.pressure.plot(label='Anemometer 1', color='red')
    anem2.pressure.plot(label='Anemometer 2', color='green')
    plt.legend()
    plt.ylim(bottom=93000, top=103000) # limits for y-axis
    plt.ylabel('Pressure (Pa)') # label for y-axis
    plt.xlabel('Time (HH:MM)') # label for x-axis
    ax.xaxis.set_major_formatter(myFmt)
    plt.title('Flight ' + plt_date_label)
    plt.show()

# This function plots all the anemometer data as an altitude time series colored by wind speed.
def plot_wind():
    plt.close('all')
    cmap = plt.cm.viridis # color map
    plt.rcParams['figure.figsize'] = (12.0, 9.0) # figure size
    fig, ax = plt.subplots()
    # plotting anem1 values
    x = anem1.index.values
    y = anem1.altitude
    c = anem1.windspeed
    plt.scatter(x=x, y=y, c=c, s=0.1)
    # plotting anem2 values
    x = anem2.index.values
    y = anem2.altitude
    c = anem2.windspeed
    plt.scatter(x=x, y=y, c=c, s=0.1)
    # axes labels
    plt.ylabel('Altitude (m)')
    plt.xlabel('Time (HH:MM)')
    # setting x-axis datetime limits
    ax.set_xlim([dt.datetime(2019, 10, 3, 12), dt.datetime(2019, 10, 3, 16)])
    # colorbar
    cb = plt.colorbar()
    cb.set_label('Wind Speed (m/s)')
    ax.xaxis.set_major_formatter(myFmt)
    plt.title('Flight ' + plt_date_label + ' ' + df_label)
    plt.savefig(plot_dir + 'eps/' + date_label + '_' + '_altitude_time_series.eps', format='eps')
    plt.savefig(plot_dir + 'png/' + date_label + '_' + '_altitude_time_series.png', format='png')

def plot_vertical_wind_profile():
    plt.close('all')
    plt.rcParams['figure.figsize'] = (12.0, 9.0)
    fig, ax = plt.subplots()
    # plot anem1 values
    x = anem1.windspeed
    y = anem1.altitude
    plt.scatter(x=x, y=y, c='blue', label='Anemometer 1', s=5)
    # plot anem2 values
    x = anem2.windspeed
    y = anem2.altitude
    plt.scatter(x=x, y=y, c='green', label='Anemometer 2', s=5)
    # plot the power law
    y = alt_list
    x = power_list
    plt.scatter(x=x, y=y, c='brown', label='Power Law', s=5)
    # plot the fitted log law
    x = fitted_list
    plt.scatter(x=x, y=y, c='black', label='Python Polyfit', s=5)
    # label the axes
    plt.xlabel('Wind Speed (m $s^{-1}$)')
    plt.ylabel('Altitude (m)')
    # legend
    legend1 = plt.scatter([],[], s=100, marker='o', color='blue')
    legend2 = plt.scatter([],[], s=100, marker='o', color='green')
    legend3 = plt.scatter([],[], s=100, marker='o', color='brown')
    legend4 = plt.scatter([],[], s=100, marker='o', color='black')
    legend = plt.legend((legend1, legend2, legend3, legend4), ('Anemometer 1', 'Anemometer 2', 'Power Law', 'Log Law'), scatterpoints=1, loc='upper left', ncol=1, fontsize=24)
    # saving the figures
    plt.savefig(plot_dir + 'svg/' + date_label + '_wind_altitude_fit_all.svg', format='svg')
    plt.savefig(plot_dir + 'eps/' + date_label + '_wind_altitude_fit_all.eps', format='eps')
    plt.savefig(plot_dir + 'png/' + date_label + '_wind_altitude_fit_all.png', format='png')

def plot_mean_vertical_wind_profile():
    plt.close('all')
    plt.rcParams['figure.figsize'] = (12.0, 9.0) # figure size
    fig, ax = plt.subplots()
    # anem1 mean values
    x = anem1_mean.windspeed
    y = anem1_mean.altitude
    plt.scatter(x=x, y=y, c='blue', label='Anemometer 1', s=100)
    # anem2 mean values
    x = anem2_mean.windspeed
    y = anem2_mean.altitude
    plt.scatter(x=x, y=y, c='green', label='Anemometer 2', s=100)
    # plot power law
    y = alt_list
    x = power_list
    plt.scatter(x=x, y=y, c='brown', label='Power Law', s=1)
    # plot log law
    x = fitted_list
    plt.scatter(x=x, y=y, c='black', label='Python Polyfit', s=1)
    # axes labels
    plt.xlabel('Wind Speed (m $s^{-1}$)')
    plt.ylabel('Altitude (m)')
    plt.legend()
    #plt.show()
    plt.savefig(plot_dir + 'svg/' + date_label + '_wind_altitude_fit_mean.svg', format='svg')
    plt.savefig(plot_dir + 'eps/' + date_label + '_wind_altitude_fit_mean.eps', format='eps')
    plt.savefig(plot_dir + 'png/' + date_label + '_wind_altitude_fit_mean.png', format='png')

# =================================================================================================
# GENERATING PLOTS ================================================================================
# =================================================================================================

# setting some parameters
myFmt = DateFormatter('%H:%M') # time formatting
plt.rcParams.update({'font.size': 24}) # font size

#print_time_of_min_pressure(time_cutoff='134500')
#plot_pressure()
#plot_wind()
#plot_vertical_wind_profile()
#plot_mean_vertical_wind_profile()
