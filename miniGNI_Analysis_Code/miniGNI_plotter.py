# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: MiniGNI Plotter
# Author: Chung Taing
# Date Updated: 13 April 2020
# Description: This script plots mini-GNI data.
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
import pandas as pd

from matplotlib.dates import DateFormatter
import miniGNI_functions as mgf

plt.close('all') # closes residual plots

# define directories
miniGNI_dir = 'C:/Users/Aaron/Dropbox/mini-GNI'
flight_dir = miniGNI_dir + '/python_scripts/miniGNI_data'

# This is the year, month, day, hour and minute when the sampling period began.
sample_year = '2019' # 4 digit year, must be string
sample_month = '05' # 2 digit month, must be string
sample_day = '19' # 2 digit day, must be string
sample_hour = '10' # 2 digit hour from 0-24, no AM/PM, must be string
sample_minute = '30' # 2 digit minute, must be string
# date allows us to specify directories
date_label = sample_year[2:] + sample_month + sample_day
sample_dir = flight_dir + '/' + sample_year + '_' + sample_month + '_' + sample_day
data_dir = sample_dir + '/data/' + date_label + '_'
plot_dir = sample_dir + '/plots'
orient_dir = plot_dir + '/orientation'
# and a date label for plot functions
plt_date_label = sample_month + '/' + sample_day + '/' + sample_year

# read in GNI data
gni1 = pd.read_csv(data_dir + 'gni1' + '.csv', header=None)
gni2 = pd.read_csv(data_dir + 'gni2' + '.csv', header=None)
gni3 = pd.read_csv(data_dir + 'gni3' + '.csv', header=None)
gni4 = pd.read_csv(data_dir + 'gni4' + '.csv', header=None)
gni5 = pd.read_csv(data_dir + 'gni5' + '.csv', header=None)

# define which XQ was at surface and which was aloft
surfaceXQ_num = '9'
aloftXQ_num = '7'

# read in XQ data
surfaceXQ = pd.read_csv(data_dir + 'surface_xq' + surfaceXQ_num + '.csv')
aloftXQ = pd.read_csv(data_dir + 'aloft_xq' + aloftXQ_num + '.csv')

# define the altitude that surface wind measurement was taken at
surface_altitude = 5

# =================================================================================================
# =================================================================================================
# =================================================================================================

# This is a correction factor to account for drift in the mini-GNI's real time clock. It has to be
# # found manually by matching up the pressure time series of the mini-GNI to that of the 
# # iMet-XQ2 instrument flying on the kite string. The iMet-XQ2 keeps time using satellite, so it
# # can be relied on. Before the correction factor is figured out, the default setting is 0.
time_corrector1 = dt.timedelta(seconds=0)
time_corrector2 = dt.timedelta(seconds=0)
time_corrector3 = dt.timedelta(seconds=0)
time_corrector4 = dt.timedelta(seconds=0)
time_corrector5 = dt.timedelta(seconds=0)

# 9/10
#time_corrector1 = dt.timedelta(seconds=-111)
#time_corrector2 = dt.timedelta(seconds=-705)
#time_corrector3 = dt.timedelta(seconds=-237)
#time_corrector4 = dt.timedelta(seconds=-336)
#time_corrector5 = dt.timedelta(seconds=73)
#time_correctorA = dt.timedelta(seconds=-218)

# 8/22
#time_corrector1 = dt.timedelta(seconds=32)
#time_corrector2 = dt.timedelta(seconds=-562)
#time_corrector3 = dt.timedelta(seconds=-151)
#time_corrector4 = dt.timedelta(seconds=-176)
#time_corrector5 = dt.timedelta(seconds=-179)

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

# turning date strings into a datetime
begin_time = dt.datetime.strptime(sample_year + sample_month + sample_day + sample_hour + sample_minute + '00', '%Y%m%d%H%M%S')

# cleaning GNI data
gni1 = mgf.clean_GNI(gni1, begin_time=begin_time, time_corrector=time_corrector1)
gni2 = mgf.clean_GNI(gni2, begin_time=begin_time, time_corrector=time_corrector2)
gni3 = mgf.clean_GNI(gni3, begin_time=begin_time, time_corrector=time_corrector3)
gni4 = mgf.clean_GNI(gni4, begin_time=begin_time, time_corrector=time_corrector4)
gni5 = mgf.clean_GNI(gni5, begin_time=begin_time, time_corrector=time_corrector5)

# cleaning XQ data
aloftXQ = mgf.clean_XQ(aloftXQ, begin_time=begin_time)
surfaceXQ = mgf.clean_XQ(surfaceXQ, begin_time=begin_time)

# correcting GNI altitude
surface_pressure = surfaceXQ['pressure'].mean()
gni1 = mgf.correct_altitude(gni1, surface_pressure=surface_pressure, surface_altitude=surface_altitude)
gni2 = mgf.correct_altitude(gni2, surface_pressure=surface_pressure, surface_altitude=surface_altitude)
gni3 = mgf.correct_altitude(gni3, surface_pressure=surface_pressure, surface_altitude=surface_altitude)
gni4 = mgf.correct_altitude(gni4, surface_pressure=surface_pressure, surface_altitude=surface_altitude)
gni5 = mgf.correct_altitude(gni5, surface_pressure=surface_pressure, surface_altitude=surface_altitude)

# RETRIEVING SAMPLE PERIODS =======================================================================

# retrieving each sample dataframe
#gni1_samples = mgf.retrieve_samples(gni1)
#gni2_samples = mgf.retrieve_samples(gni2)
#gni3_samples = mgf.retrieve_samples(gni3)
#gni4_samples = mgf.retrieve_samples(gni4)
#gni5_samples = mgf.retrieve_samples(gni5)

#gni1s1 = gni1_samples[0]
#gni1s2 = gni1_samples[1]
#gni1s3 = gni1_samples[2]

#gni2s1 = gni2_samples[0]
#gni2s2 = gni2_samples[1]
#gni2s3 = gni2_samples[2]

#gni3s1 = gni3_samples[0]
#gni3s2 = gni3_samples[1]
#gni3s3 = gni3_samples[2]

#gni4s1 = gni4_samples[0]
#gni4s2 = gni4_samples[1]
#gni4s3 = gni4_samples[2]

#gni5s1 = gni5_samples[0]
#gni5s2 = gni5_samples[1]
#gni5s3 = gni5_samples[2]

# MANUALLY FIND TIME CORRECTION ===================================================================

# prints minimum pressure of mini-GNI data sets and iMet-XQ2 data set
def print_time_of_minimum_pressure(time_cutoff):
    end_time = dt.datetime.strptime(date_label + time_cutoff, '%y%m%d%H%M%S')
    print(gni1[gni1.index < end_time].pressure.idxmin(axis=0))
    print(gni2[gni2.index < end_time].pressure.idxmin(axis=0))
    print(gni3[gni3.index < end_time].pressure.idxmin(axis=0))
    print(gni4[gni4.index < end_time].pressure.idxmin(axis=0))
    print(gni5[gni5.index < end_time].pressure.idxmin(axis=0))
    print(aloftXQ[aloftXQ.index < end_time].pressure.idxmin(axis=0))

# plotting pressure to assist in finding correct "time_corrector"
def plot_pressure():
    myFmt = DateFormatter('%H:%M')
    plt.rcParams['figure.figsize'] = (12.0, 6.75)
    fig, ax = plt.subplots()
    surfaceXQ.pressure.plot(label = 'XQ Surface', color='grey')
    aloftXQ.pressure.plot(label='XQ Aloft', color='black')
    gni1.pressure.plot(label='GNI 1', color='red')
    gni2.pressure.plot(label='GNI 2', color='orange')
    gni3.pressure.plot(label='GNI 3', color='green')
    gni4.pressure.plot(label='GNI 4', color='blue')
    gni5.pressure.plot(label='GNI 5', color='purple')
    plt.legend()
    plt.ylim(bottom=93000, top=103000)
    plt.ylabel('Pressure (Pa)')
    plt.xlabel('Time (HH:MM)')
    ax.xaxis.set_major_formatter(myFmt)
    plt.title('Flight ' + plt_date_label)
    plt.show()

# uncomment the following to manually determine what time_corrector should be
#print_time_of_minimum_pressure(time_cutoff = '100000')
#plot_pressure()

# PLOTTING ========================================================================================

# setting date format
myFmt = DateFormatter('%H:%M')

# plots a time series of a variable that you want, defined by variable_label
def plot_time_series(variable_label, y_label):
    plt.rcParams['figure.figsize'] = (16.0, 9.0)
    fig, ax = plt.subplots()
    if not variable_label == 'alpha':
        surfaceXQ[variable_label].plot(label='XQ Surface', color='grey')
        aloftXQ[variable_label].plot(label='XQ Aloft', color='black')
    gni1[variable_label].plot(label='GNI 1', color='red')
    gni2[variable_label].plot(label='GNI 2', color='orange')
    if not variable_label == 'alpha':
        gni3[variable_label].plot(label='GNI 3', color='green')
        gni4[variable_label].plot(label='GNI 4', color='blue')
    gni5[variable_label].plot(label='GNI 5', color='purple')
    plt.legend()
    plt.ylabel(y_label)
    plt.xlabel('Time (HH:MM)')
    ax.xaxis.set_major_formatter(myFmt)
    plt.title('Flight ' + plt_date_label)
    plt.savefig(plot_dir + '/svg/' + date_label + '_' + variable_label + '_time_series.svg', format='svg')
    plt.savefig(plot_dir + '/eps/' + date_label + '_' + variable_label + '_time_series.eps', format='eps')
    plt.savefig(plot_dir + '/png/' + date_label + '_' + variable_label + '_time_series.png', format='png')
    plt.close('all')

#plot_time_series(variable_label='altitude', y_label='Altitude (m)')
#plot_time_series(variable_label='kelvinT', y_label='Temperature (K)')
#plot_time_series(variable_label='rh', y_label='Humidity (%)')
#plot_time_series(variable_label='alpha', y_label='Alpha Angle (rad)')

#PLOTTING ORIENTATION==============================================================================

# plot orientation (alpha, beta, gamma) of each mini-GNI sample performed by an instrument with
# # an orientation sensor
def plot_orientation(df, gni_number, sample_number, number_bins):
    plt.rcParams['figure.figsize'] = (16.0, 9.0)
    plot_title = 'GNI ' + str(gni_number) + ' Sample ' + str(sample_number) + ' Orientation Histogram ' + str(sample_month) + '/' + str(sample_day) + '/' + str(sample_year)
    bins = np.linspace(0.0, 2*np.pi, number_bins, endpoint=False)
    fig = plt.figure()
    fig.suptitle(plot_title)
    # alpha plot
    ax1 = fig.add_subplot(1, 3, 1, projection='polar')
    ax1.hist(df.alpha, bins)
    ax1.set_title('Alpha')
    # beta plot
    ax2 = fig.add_subplot(1, 3, 2, projection='polar')
    ax2.hist(df.beta, bins)
    ax2.set_title('Beta')
    # gamma plot
    ax3 = fig.add_subplot(1, 3, 3, projection='polar')
    ax3.hist(df.gamma, bins)
    ax3.set_title('Gamma')
    plt.tight_layout()
    # save plot
    plt.savefig(orient_dir + '/' + date_label + '_gni' + str(gni_number) + 's' + str(sample_number) + 'OrientHisto.png', format='png')
    plt.savefig(orient_dir + '/eps/' + date_label + '_gni' + str(gni_number) + 's' + str(sample_number) + 'OrientHisto.eps', format='eps')
    plt.close('all')

#plot_orientation(df=gni1s1, gni_number=1, sample_number=1, number_bins=64)
#plot_orientation(df=gni1s2, gni_number=1, sample_number=2, number_bins=64)
#plot_orientation(df=gni1s3, gni_number=1, sample_number=3, number_bins=64)
#plot_orientation(df=gni2s1, gni_number=2, sample_number=1, number_bins=64)
#plot_orientation(df=gni2s2, gni_number=2, sample_number=2, number_bins=64)
#plot_orientation(df=gni2s3, gni_number=2, sample_number=3, number_bins=64)
#plot_orientation(df=gni5s1, gni_number=5, sample_number=1, number_bins=64)
#plot_orientation(df=gni5s2, gni_number=5, sample_number=2, number_bins=64)
#plot_orientation(df=gni5s3, gni_number=5, sample_number=3, number_bins=64)
