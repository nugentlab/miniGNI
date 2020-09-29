# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: SSA Plotter
# Author: Chung Taing
# Date Updated: 10 April 2020
# Description: This script contains functions required to plot processed sample data. Sample data
# is processed by SSA Data Saver.
# =================================================================================================
# =================================================================================================
# =================================================================================================

# import packages and functions
import colorcet as cc
import datetime as dt
import math
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import pandas as pd

from ast import literal_eval
from matplotlib.dates import DateFormatter
from scipy import stats
from scipy.optimize import curve_fit
from lmfit.models import ExpressionModel

import ranzwong as rw
import ssa_plot_functions as spf

plt.close('all') # closing any residual plot data before continuing

# =================================================================================================
# =================================================================================================
# =================================================================================================
# LOADING DATA ====================================================================================
# =================================================================================================

# define directories
miniGNI_dir = 'C:/Users/ntril/Dropbox/mini-GNI'
data_dir = miniGNI_dir + '/python_scripts/data'
plot_dir = miniGNI_dir + '/python_scripts/plots'

# loading data
ssaData = pd.read_csv(data_dir + '/ssaDF_final.csv')
vocalsData = pd.read_csv(data_dir + '/vocalsDF.csv')
synthData = pd.read_csv(data_dir + '/synthDF.csv')

def apply_literal_eval(df):
    # changing id_number to string
    df['id_number'] = df['id_number'].astype(str)
    # changing datetime columns that read as objects to datetime
    df['date'] = pd.to_datetime(df['date'])
    df['timedate'] = pd.to_datetime(df['timedate'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    # changing list columns that read as objects to lists
    df['bin_number'] = df['bin_number'].apply(literal_eval)
    df['bin_lower'] = df['bin_lower'].apply(literal_eval)
    df['bin_middle'] = df['bin_middle'].apply(literal_eval)
    df['bin_upper'] = df['bin_upper'].apply(literal_eval)
    df['bin_conc'] = df['bin_conc'].apply(literal_eval)
    df['cumu_conc'] = df['cumu_conc'].apply(literal_eval)
    df['bin_salt'] = df['bin_salt'].apply(literal_eval)
    df['bin_fixed_conc'] = df['bin_fixed_conc'].apply(literal_eval)
    df['bin_ce'] = df['bin_ce'].apply(literal_eval)
    df['bin_real_conc'] = df['bin_real_conc'].apply(literal_eval)
    df['real_cumu_conc'] = df['real_cumu_conc'].apply(literal_eval)
    df['bin_real_salt'] = df['bin_real_salt'].apply(literal_eval)
    # some data sets don't have this data
    try: 
        df['tide_time'] = pd.to_datetime(df['tide_time'])
        df['phng_time'] = pd.to_datetime(df['phng_time'])
        df['bin_cutoff_salt'] = df['bin_cutoff_salt'].apply(literal_eval)
        df['bin_cutoff_conc'] = df['bin_cutoff_conc'].apply(literal_eval)
        df['cutoff_cumu_conc'] = df['cutoff_cumu_conc'].apply(literal_eval)
        df['highwind_ce'] = df['highwind_ce'].apply(literal_eval)
        df['highwind_conc'] = df['highwind_conc'].apply(literal_eval)
        df['lowwind_ce'] = df['lowwind_ce'].apply(literal_eval)
        df['lowwind_conc'] = df['lowwind_conc'].apply(literal_eval)
    finally:
        return df

ssaData = apply_literal_eval(df=ssaData)
vocalsData = apply_literal_eval(df=vocalsData)
synthData = apply_literal_eval(df=synthData)
synthData['synth_ce'] = synthData['synth_ce'].apply(literal_eval)
synthData['synth_conc'] = synthData['synth_conc'].apply(literal_eval)

# setting index to be datetime
ssaData.set_index('timedate', drop=True, inplace=True)
vocalsData.set_index('timedate', drop=True, inplace=True)
synthData.set_index('timedate', drop=True, inplace=True)

# =================================================================================================
# =================================================================================================
# =================================================================================================
# WOODCOCK DATA ==================================================================================
# =================================================================================================

woodcock_49_1 = pd.read_csv(data_dir + '/woodcock_data/woodcock_49_1.csv', header=None)
woodcock_42_3 = pd.read_csv(data_dir + '/woodcock_data/woodcock_42_3.csv', header=None)
woodcock_36_4 = pd.read_csv(data_dir + '/woodcock_data/woodcock_36_4.csv', header=None)
woodcock_39_5 = pd.read_csv(data_dir + '/woodcock_data/woodcock_39_5.csv', header=None)
woodcock_35_7 = pd.read_csv(data_dir + '/woodcock_data/woodcock_35_7.csv', header=None)
woodcock_22_12 = pd.read_csv(data_dir + '/woodcock_data/woodcock_22_12.csv', header=None)

def process_woodcock_data(df):
    df.columns = ['dry_radius', 'n_concentration']
    df.dry_radius = np.power(10, df.dry_radius)
    df.n_concentration = np.power(10, df.n_concentration)
    df.dry_radius = df.dry_radius*1e-15
    df.dry_radius = np.power((3/4)*df.dry_radius/(math.pi*1.78e3), (1/3))
    df.dry_radius = df.dry_radius*1e6
    return df

w_49_1 = process_woodcock_data(woodcock_49_1)
w_42_3 = process_woodcock_data(woodcock_42_3)
w_39_5 = process_woodcock_data(woodcock_39_5)
w_35_7 = process_woodcock_data(woodcock_35_7)
w_22_12 = process_woodcock_data(woodcock_22_12)

# =================================================================================================
# =================================================================================================
# =================================================================================================
# PLOTS ===========================================================================================
# =================================================================================================
# =================================================================================================
# =================================================================================================
# Publication Plots
if False:
    # Figure 4
    spf.plot_ranz_wong(plot_resolution=50, max_radius=15, max_wind_speed=15)
    spf.plot_ranz_wong(plot_resolution=100, max_radius=5, max_wind_speed=5)
    # Figure 5
    spf.plot_size_distribution(df=vocalsData, id_num='081018a3')
    spf.plot_size_distribution(df=ssaData, id_num='190731a1')
    # Figure 6
    spf.plot_lognormal_stats(df=ssaData, df2=vocalsData)
    # Figure 7
    spf.plot_cumulative_concentration_average(df=ssaData, color_variable='altitude', cutoff_list=[10, 25, 55, 125, 200, 300, 400, 500, 700], color_label='Altitude (m)')
    spf.plot_total_concentration(df=ssaData, y_variable='cutoff_total_conc', x_variable='altitude', color_variable='surface_wind', size_variable='wave_height', x_label='Altitude (m)', color_label='Surface Wind Speed (m $\mathrm{s^{-1}}$)', size_label='Significant Wave Height (m)')
    # Figure 8
    spf.plot_compare_woodcock_average(df=ssaData, wdf1=w_49_1, wdf2=w_42_3, wdf3=w_39_5, wdf4=w_35_7, wdf5=w_22_12, cutoff_winds=[3.0,3.5,4.0,4.5,5.0,5.5,6.0], y_variable = 'cutoff_cumu_conc')
    spf.plot_total_concentration(df=ssaData, y_variable='cutoff_total_conc', x_variable='surface_wind', color_variable='altitude', size_variable='wave_height', x_label='Surface Wind Speed (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')
    spf.plot_total_concentration(df=ssaData, y_variable='cutoff_total_conc', x_variable='phng_wind12hr', color_variable='altitude', size_variable='wave_height', x_label='Kaneohe 12hr Mean 10m Wind (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')
    # Figure 9
    spf.plot_wind_sensitivity(df=ssaData, id_num='190413a5')
    # Figure 11
    spf.plot_cumulative_concentration_average(df=ssaData, color_variable='wave_height', cutoff_list=[1.2, 1.5, 2.0, 2.6, 3.7], color_label='Wave Height (m)')
    spf.plot_total_concentration(df=ssaData, y_variable='cutoff_total_conc', x_variable='wave_height', color_variable='altitude', size_variable='surface_wind', x_label='Significant Wave Height (m)', color_label='Altitude (m)', size_label='Surface Wind Speed (m $\mathrm{s^{-1}}$)')




# =================================================================================================
# PLOT ALL SAMPLES OVER TIME BY ALTITUDE ==========================================================
# =================================================================================================

if False:
    spf.plot_all_samples(df=ssaData, color_variable='surface_wind', color_label='Surface Wind Speed (m/s)')
    spf.plot_all_samples(df=ssaData, color_variable='duration', color_label='Duration (min)')
    spf.plot_all_samples(df=ssaData, color_variable='wave_height', color_label='Sig. Wave Height (m)')
    spf.plot_all_samples(df=ssaData, color_variable='rh', color_label='Relative Humidity (%)')
    spf.plot_mass_distribution_tenpercent(df=ssaData)

# =================================================================================================
# PLOT CUMULATIVE CONCENTRATION ===================================================================
# =================================================================================================

#spf.plot_compare_woodcock_average(df=vocalsData, wdf1=w_49_1, wdf2=w_42_3, wdf3=w_39_5, wdf4=w_35_7, wdf5=w_22_12, cutoff_winds=[0.6,2.0,4.0,6.0,8.0,10.0,12.0,17.5], y_variable = 'cumu_conc')
#spf.plot_cumulative_concentration_average(df=ssaData, color_variable='wave_height', cutoff_list=[1.2, 1.5, 2.0, 2.6, 3.7], color_label='Wave Height (m)')
#spf.plot_compare_woodcock_average(df=ssaData, wdf1=w_49_1, wdf2=w_42_3, wdf3=w_39_5, wdf4=w_35_7, wdf5=w_22_12, cutoff_winds=[3.0,3.5,4.0,4.5,5.0,5.5,6.0], y_variable = 'cutoff_cumu_conc')

if False:
    spf.plot_cumulative_concentration(df=ssaData, color_variable='surface_wind', color_label='Surface Wind Speed (m $s^{-1}$)')
    spf.plot_cumulative_concentration(df=ssaData, color_variable='altitude', color_label='Altitude (m)')
    spf.plot_cumulative_concentration(df=ssaData, color_variable='wave_height', color_label='Significant Wave Height (m)')
    spf.plot_cumulative_concentration_average(df=ssaData, color_variable='altitude', cutoff_list=[10, 25, 55, 125, 200, 300, 400, 500, 700], color_label='Altitude (m)')
    spf.plot_cumulative_concentration_average(df=ssaData, color_variable='wave_height', cutoff_list=[1.2, 1.5, 2.0, 2.6, 3.7], color_label='Wave Height (m)')
    spf.plot_compare_woodcock(df=ssaData, wdf1=w_49_1, wdf2=w_42_3, wdf3=w_39_5, wdf4=w_35_7, wdf5=w_22_12)
    spf.plot_compare_woodcock_average(df=ssaData, wdf1=w_49_1, wdf2=w_42_3, wdf3=w_39_5, wdf4=w_35_7, wdf5=w_22_12, cutoff_winds=[3.0,3.5,4.0,4.5,5.0,5.5,6.0], y_variable = 'cutoff_cumu_conc')
    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='phng_wind12hr', color_variable='altitude', size_variable='wave_height', x_label='Kaneohe 12hr Mean 10m Wind (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')


# =================================================================================================
# PLOT WIND OR WAVE DIRECTION =====================================================================
# =================================================================================================

if False:
    spf.plot_wind_vs_waves(df=ssaData)
    spf.plot_wave_orientation(df=ssaData, number_bins=72)
    spf.plot_wind_orientation(df=ssaData, number_bins=72)

# =================================================================================================
# PLOT LOGNORMAL STATS HISTOGRAMS =================================================================
# =================================================================================================
if False:
    spf.plot_lognormal_stats(df=ssaData, df2=vocalsData)
    #spf.plot_lognormal_comparison(df=vocalsData)

# =================================================================================================
# CORRELATION PLOTS ===============================================================================
# =================================================================================================

if False:
    spf.plot_correlation(df=ssaData, x_variable='surface_wind', y_variable='wave_height', x_label='Surface Wind Speed (m/s)', y_label='Significant Wave Height (m)')
    spf.plot_correlation(df=ssaData, x_variable='phng_wind', y_variable='wave_height', x_label='Kaneohe 10m Wind (m/s)', y_label='Significant Wave Height (m)')
    spf.plot_correlation(df=ssaData, x_variable='phng_wind6hr', y_variable='wave_height', x_label='Kaneohe 6hr 10m Wind (m/s)', y_label='Significant Wave Height (m)')
    spf.plot_correlation(df=ssaData, x_variable='phng_wind12hr', y_variable='wave_height', x_label='Kaneohe 12hr 10m Wind (m/s)', y_label='Significant Wave Height (m)')
    spf.plot_correlation(df=ssaData, x_variable='phng_wind24hr', y_variable='wave_height', x_label='Kaneohe 24hr 10m Wind (m/s)', y_label='Significant Wave Height (m)')
    spf.plot_correlation(df=ssaData, x_variable='phng_wind48hr', y_variable='wave_height', x_label='Kaneohe 48hr 10m Wind (m/s)', y_label='Significant Wave Height (m)')
    spf.plot_correlation(df=ssaData, x_variable='phng_wind72hr', y_variable='wave_height', x_label='Kaneohe 72hr 10m Wind (m/s)', y_label='Significant Wave Height (m)')

# =================================================================================================
# TOTAL NUMBER CONCENTRATION FOR PARTICLES GREATER THAN OR EQUAL TO A CUTOFF RADIUS ===============
# =================================================================================================

# set what you want your y variable to be
# # it must be a type of total concentration
#y_variable = 'cutoff_total_conc'
#y_variable = 'lowwind_total_conc'
#y_variable = 'real_total_conc'
#y_variable = 'cutoff_total_mass'
y_variable = 'real_total_salt'

if False:

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='tide_level', color_variable='altitude', size_variable='wave_height', x_label='Tide Level (m)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='altitude', color_variable='surface_wind', size_variable='wave_height', x_label='Altitude (m)', color_label='Surface Wind Speed (m $\mathrm{s^{-1}}$)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='surface_wind', color_variable='altitude', size_variable='wave_height', x_label='Surface Wind Speed (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='wave_height', color_variable='altitude', size_variable='surface_wind', x_label='Significant Wave Height (m)', color_label='Altitude (m)', size_label='Surface Wind Speed (m $\mathrm{s^{-1}}$)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='peak_period', color_variable='altitude', size_variable='wave_height', x_label='Peak Period (s)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='mean_period', color_variable='altitude', size_variable='wave_height', x_label='Mean Period (s)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='rh', color_variable='altitude', size_variable='wave_height', x_label='Relative Humidity (%)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='phng_wind', color_variable='altitude', size_variable='wave_height', x_label='Kaneohe 10 meter Wind (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='phng_wind6hr', color_variable='altitude', size_variable='wave_height', x_label='Kaneohe 6hr Mean 10m Wind (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='phng_wind12hr', color_variable='altitude', size_variable='wave_height', x_label='Kaneohe 12hr Mean 10m Wind (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='phng_wind24hr', color_variable='altitude', size_variable='wave_height', x_label='Kaneohe 24hr Mean 10m Wind (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='phng_wind48hr', color_variable='altitude', size_variable='wave_height', x_label='Kaneohe 48hr Mean 10m Wind (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='phng_wind72hr', color_variable='altitude', size_variable='wave_height', x_label='Kaneohe 72hr Mean 10m Wind (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

    spf.plot_total_concentration(df=ssaData, y_variable=y_variable, x_variable='phng_wind120hr', color_variable='altitude', size_variable='wave_height', x_label='Kaneohe 120hr Mean 10m Wind (m $\mathrm{s^{-1}}$)', color_label='Altitude (m)', size_label='Significant Wave Height (m)')

# =================================================================================================
# CUMULATIVE CONCENTRATION BY SIZE WITH ALTITUDE FOR INDIVIDUAL SAMPLE DAYS========================
# =================================================================================================

if False:
    spf.plot_sample_day_concentration(df=ssaData, sample_date='181205')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190101')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190413')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190423')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190519')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190616')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190731')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190815')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190820')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190822')
    spf.plot_sample_day_concentration(df=ssaData, sample_date='190910')

if False:
    spf.plot_sample_day_concentration_average(df=ssaData, sample_date='181205')
    spf.plot_sample_day_concentration_average(df=ssaData, sample_date='190101')
    spf.plot_sample_day_concentration_average(df=ssaData, sample_date='190413')
    spf.plot_sample_day_concentration_average(df=ssaData, sample_date='190423')
    spf.plot_sample_day_concentration_average(df=ssaData, sample_date='190731')
    spf.plot_sample_day_concentration_average(df=ssaData, sample_date='190815')
    spf.plot_sample_day_concentration_average(df=ssaData, sample_date='190820')
    spf.plot_sample_day_concentration_average(df=ssaData, sample_date='190822')
    spf.plot_sample_day_concentration_average(df=ssaData, sample_date='190910')

# =================================================================================================
# SIZE DISTRIBUTION HISTOGRAMS WITH LOGNORMAL FITS=================================================
# =================================================================================================

if False:
    spf.plot_size_distribution(df=ssaData, id_num='181205a1')
    spf.plot_size_distribution(df=ssaData, id_num='181205a2')
    spf.plot_size_distribution(df=ssaData, id_num='181205a4')
    spf.plot_size_distribution(df=ssaData, id_num='181205a5')
    spf.plot_size_distribution(df=ssaData, id_num='181205a6')
    spf.plot_size_distribution(df=ssaData, id_num='181205a7')
    spf.plot_size_distribution(df=ssaData, id_num='181205a8')

    spf.plot_size_distribution(df=ssaData, id_num='190101a1')
    spf.plot_size_distribution(df=ssaData, id_num='190101a2')
    spf.plot_size_distribution(df=ssaData, id_num='190101a3')
    spf.plot_size_distribution(df=ssaData, id_num='190101a4')

    spf.plot_size_distribution(df=ssaData, id_num='190413a1')
    spf.plot_size_distribution(df=ssaData, id_num='190413a2')
    spf.plot_size_distribution(df=ssaData, id_num='190413a3')
    spf.plot_size_distribution(df=ssaData, id_num='190413a4')
    spf.plot_size_distribution(df=ssaData, id_num='190413a5')
    spf.plot_size_distribution(df=ssaData, id_num='190413a6')
    spf.plot_size_distribution(df=ssaData, id_num='190413a8')

    spf.plot_size_distribution(df=ssaData, id_num='190423a1')
    spf.plot_size_distribution(df=ssaData, id_num='190423a2')
    spf.plot_size_distribution(df=ssaData, id_num='190423a3')
    spf.plot_size_distribution(df=ssaData, id_num='190423a4')
    spf.plot_size_distribution(df=ssaData, id_num='190423a5')
    spf.plot_size_distribution(df=ssaData, id_num='190423a7')

    spf.plot_size_distribution(df=ssaData, id_num='190519a1')
    spf.plot_size_distribution(df=ssaData, id_num='190519a2')

    spf.plot_size_distribution(df=ssaData, id_num='190616a1')
    spf.plot_size_distribution(df=ssaData, id_num='190616a4')

    spf.plot_size_distribution(df=ssaData, id_num='190731a1')
    spf.plot_size_distribution(df=ssaData, id_num='190731a2')
    spf.plot_size_distribution(df=ssaData, id_num='190731a3')
    spf.plot_size_distribution(df=ssaData, id_num='190731a4')
    spf.plot_size_distribution(df=ssaData, id_num='190731a5')
    spf.plot_size_distribution(df=ssaData, id_num='190731a6')
    spf.plot_size_distribution(df=ssaData, id_num='190731a7')
    spf.plot_size_distribution(df=ssaData, id_num='190731a8')
    spf.plot_size_distribution(df=ssaData, id_num='190731a9')
    spf.plot_size_distribution(df=ssaData, id_num='190731a10')
    spf.plot_size_distribution(df=ssaData, id_num='190731a11')
    spf.plot_size_distribution(df=ssaData, id_num='190731a12')

    spf.plot_size_distribution(df=ssaData, id_num='190815a1')
    spf.plot_size_distribution(df=ssaData, id_num='190815a2')
    spf.plot_size_distribution(df=ssaData, id_num='190815a3')
    spf.plot_size_distribution(df=ssaData, id_num='190815a4')
    spf.plot_size_distribution(df=ssaData, id_num='190815a5')
    spf.plot_size_distribution(df=ssaData, id_num='190815a6')
    spf.plot_size_distribution(df=ssaData, id_num='190815a7')
    spf.plot_size_distribution(df=ssaData, id_num='190815a8')
    spf.plot_size_distribution(df=ssaData, id_num='190815a9')
    spf.plot_size_distribution(df=ssaData, id_num='190815a10')
    spf.plot_size_distribution(df=ssaData, id_num='190815a11')
    spf.plot_size_distribution(df=ssaData, id_num='190815a12')
    spf.plot_size_distribution(df=ssaData, id_num='190815a13')
    spf.plot_size_distribution(df=ssaData, id_num='190815a14')
    spf.plot_size_distribution(df=ssaData, id_num='190815a15')

    spf.plot_size_distribution(df=ssaData, id_num='190820a1')
    spf.plot_size_distribution(df=ssaData, id_num='190820a2')
    spf.plot_size_distribution(df=ssaData, id_num='190820a3')
    spf.plot_size_distribution(df=ssaData, id_num='190820a4')
    spf.plot_size_distribution(df=ssaData, id_num='190820a5')
    spf.plot_size_distribution(df=ssaData, id_num='190820a6')
    spf.plot_size_distribution(df=ssaData, id_num='190820a7')
    spf.plot_size_distribution(df=ssaData, id_num='190820a8')
    spf.plot_size_distribution(df=ssaData, id_num='190820a9')
    spf.plot_size_distribution(df=ssaData, id_num='190820a10')
    spf.plot_size_distribution(df=ssaData, id_num='190820a11')
    spf.plot_size_distribution(df=ssaData, id_num='190820a14')
    spf.plot_size_distribution(df=ssaData, id_num='190820a15')

    spf.plot_size_distribution(df=ssaData, id_num='190822a1')
    spf.plot_size_distribution(df=ssaData, id_num='190822a2')
    spf.plot_size_distribution(df=ssaData, id_num='190822a3')
    spf.plot_size_distribution(df=ssaData, id_num='190822a4')
    spf.plot_size_distribution(df=ssaData, id_num='190822a5')
    spf.plot_size_distribution(df=ssaData, id_num='190822a6')
    spf.plot_size_distribution(df=ssaData, id_num='190822a7')
    spf.plot_size_distribution(df=ssaData, id_num='190822a8')
    spf.plot_size_distribution(df=ssaData, id_num='190822a9')
    spf.plot_size_distribution(df=ssaData, id_num='190822a10')
    spf.plot_size_distribution(df=ssaData, id_num='190822a11')
    spf.plot_size_distribution(df=ssaData, id_num='190822a12')
    spf.plot_size_distribution(df=ssaData, id_num='190822a13')
    spf.plot_size_distribution(df=ssaData, id_num='190822a14')
    spf.plot_size_distribution(df=ssaData, id_num='190822a15')

    spf.plot_size_distribution(df=ssaData, id_num='190910a1')
    spf.plot_size_distribution(df=ssaData, id_num='190910a2')
    spf.plot_size_distribution(df=ssaData, id_num='190910a3')
    spf.plot_size_distribution(df=ssaData, id_num='190910a4')
    spf.plot_size_distribution(df=ssaData, id_num='190910a5')
    spf.plot_size_distribution(df=ssaData, id_num='190910a6')
    spf.plot_size_distribution(df=ssaData, id_num='190910a7')
    spf.plot_size_distribution(df=ssaData, id_num='190910a8')
    spf.plot_size_distribution(df=ssaData, id_num='190910a10')
    spf.plot_size_distribution(df=ssaData, id_num='190910a11')
    spf.plot_size_distribution(df=ssaData, id_num='190910a12')
    spf.plot_size_distribution(df=ssaData, id_num='190910a13')


# =================================================================================================
# SIZE DISTRIBUTION HISTOGRAMS SHOWING WIND SENSITIVITY TEST ======================================
# =================================================================================================
if False:
    spf.plot_wind_sensitivity(df=ssaData, id_num='181205a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='181205a2')
    spf.plot_wind_sensitivity(df=ssaData, id_num='181205a4')
    spf.plot_wind_sensitivity(df=ssaData, id_num='181205a5')
    spf.plot_wind_sensitivity(df=ssaData, id_num='181205a6')
    spf.plot_wind_sensitivity(df=ssaData, id_num='181205a7')
    spf.plot_wind_sensitivity(df=ssaData, id_num='181205a8')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190101a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190101a2')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190101a3')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190101a4')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190413a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190413a2')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190413a3')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190413a4')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190413a5')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190413a6')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190413a8')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190423a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190423a2')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190423a3')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190423a4')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190423a5')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190423a7')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190519a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190519a2')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190616a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190616a4')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a2')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a3')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a4')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a5')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a6')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a7')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a8')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a9')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a10')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a11')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190731a12')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a2')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a3')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a4')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a5')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a6')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a7')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a8')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a9')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a10')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a11')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a12')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a13')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a14')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190815a15')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a2')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a3')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a4')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a5')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a6')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a7')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a8')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a9')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a10')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a11')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a14')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190820a15')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a2')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a3')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a4')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a5')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a6')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a7')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a8')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a9')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a10')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a11')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a12')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a13')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a14')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190822a15')

    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a1')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a2')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a3')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a4')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a5')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a6')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a7')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a8')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a10')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a11')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a12')
    spf.plot_wind_sensitivity(df=ssaData, id_num='190910a13')

# =================================================================================================
# SYNTH SIZE DISTRIBUTION HISTOGRAMS WITH LOGNORMAL FITS=================================================
# =================================================================================================

if False:
    spf.plot_synth_distribution(df=synthData, id_num='181205a1')
    spf.plot_synth_distribution(df=synthData, id_num='181205a2')
    spf.plot_synth_distribution(df=synthData, id_num='181205a4')
    spf.plot_synth_distribution(df=synthData, id_num='181205a5')
    spf.plot_synth_distribution(df=synthData, id_num='181205a6')
    spf.plot_synth_distribution(df=synthData, id_num='181205a7')
    spf.plot_synth_distribution(df=synthData, id_num='181205a8')

    spf.plot_synth_distribution(df=synthData, id_num='190101a1')
    spf.plot_synth_distribution(df=synthData, id_num='190101a2')
    spf.plot_synth_distribution(df=synthData, id_num='190101a3')
    spf.plot_synth_distribution(df=synthData, id_num='190101a4')

    spf.plot_synth_distribution(df=synthData, id_num='190413a1')
    spf.plot_synth_distribution(df=synthData, id_num='190413a2')
    spf.plot_synth_distribution(df=synthData, id_num='190413a3')
    spf.plot_synth_distribution(df=synthData, id_num='190413a4')
    spf.plot_synth_distribution(df=synthData, id_num='190413a5')
    spf.plot_synth_distribution(df=synthData, id_num='190413a6')
    spf.plot_synth_distribution(df=synthData, id_num='190413a8')

    spf.plot_synth_distribution(df=synthData, id_num='190423a1')
    spf.plot_synth_distribution(df=synthData, id_num='190423a2')
    spf.plot_synth_distribution(df=synthData, id_num='190423a3')
    spf.plot_synth_distribution(df=synthData, id_num='190423a4')
    spf.plot_synth_distribution(df=synthData, id_num='190423a5')
    spf.plot_synth_distribution(df=synthData, id_num='190423a7')

    spf.plot_synth_distribution(df=synthData, id_num='190519a1')
    spf.plot_synth_distribution(df=synthData, id_num='190519a2')

    spf.plot_synth_distribution(df=synthData, id_num='190616a1')
    spf.plot_synth_distribution(df=synthData, id_num='190616a4')

    spf.plot_synth_distribution(df=synthData, id_num='190731a1')
    spf.plot_synth_distribution(df=synthData, id_num='190731a2')
    spf.plot_synth_distribution(df=synthData, id_num='190731a3')
    spf.plot_synth_distribution(df=synthData, id_num='190731a4')
    spf.plot_synth_distribution(df=synthData, id_num='190731a5')
    spf.plot_synth_distribution(df=synthData, id_num='190731a6')
    spf.plot_synth_distribution(df=synthData, id_num='190731a7')
    spf.plot_synth_distribution(df=synthData, id_num='190731a8')
    spf.plot_synth_distribution(df=synthData, id_num='190731a9')
    spf.plot_synth_distribution(df=synthData, id_num='190731a10')
    spf.plot_synth_distribution(df=synthData, id_num='190731a11')
    spf.plot_synth_distribution(df=synthData, id_num='190731a12')

    spf.plot_synth_distribution(df=synthData, id_num='190815a1')
    spf.plot_synth_distribution(df=synthData, id_num='190815a2')
    spf.plot_synth_distribution(df=synthData, id_num='190815a3')
    spf.plot_synth_distribution(df=synthData, id_num='190815a4')
    spf.plot_synth_distribution(df=synthData, id_num='190815a5')
    spf.plot_synth_distribution(df=synthData, id_num='190815a6')
    spf.plot_synth_distribution(df=synthData, id_num='190815a7')
    spf.plot_synth_distribution(df=synthData, id_num='190815a8')
    spf.plot_synth_distribution(df=synthData, id_num='190815a9')
    spf.plot_synth_distribution(df=synthData, id_num='190815a10')
    spf.plot_synth_distribution(df=synthData, id_num='190815a11')
    spf.plot_synth_distribution(df=synthData, id_num='190815a12')
    spf.plot_synth_distribution(df=synthData, id_num='190815a13')
    spf.plot_synth_distribution(df=synthData, id_num='190815a14')
    spf.plot_synth_distribution(df=synthData, id_num='190815a15')

    spf.plot_synth_distribution(df=synthData, id_num='190820a1')
    spf.plot_synth_distribution(df=synthData, id_num='190820a2')
    spf.plot_synth_distribution(df=synthData, id_num='190820a3')
    spf.plot_synth_distribution(df=synthData, id_num='190820a4')
    spf.plot_synth_distribution(df=synthData, id_num='190820a5')
    spf.plot_synth_distribution(df=synthData, id_num='190820a6')
    spf.plot_synth_distribution(df=synthData, id_num='190820a7')
    spf.plot_synth_distribution(df=synthData, id_num='190820a8')
    spf.plot_synth_distribution(df=synthData, id_num='190820a9')
    spf.plot_synth_distribution(df=synthData, id_num='190820a10')
    spf.plot_synth_distribution(df=synthData, id_num='190820a11')
    spf.plot_synth_distribution(df=synthData, id_num='190820a14')
    spf.plot_synth_distribution(df=synthData, id_num='190820a15')

    spf.plot_synth_distribution(df=synthData, id_num='190822a1')
    spf.plot_synth_distribution(df=synthData, id_num='190822a2')
    spf.plot_synth_distribution(df=synthData, id_num='190822a3')
    spf.plot_synth_distribution(df=synthData, id_num='190822a4')
    spf.plot_synth_distribution(df=synthData, id_num='190822a5')
    spf.plot_synth_distribution(df=synthData, id_num='190822a6')
    spf.plot_synth_distribution(df=synthData, id_num='190822a7')
    spf.plot_synth_distribution(df=synthData, id_num='190822a8')
    spf.plot_synth_distribution(df=synthData, id_num='190822a9')
    spf.plot_synth_distribution(df=synthData, id_num='190822a10')
    spf.plot_synth_distribution(df=synthData, id_num='190822a11')
    spf.plot_synth_distribution(df=synthData, id_num='190822a12')
    spf.plot_synth_distribution(df=synthData, id_num='190822a13')
    spf.plot_synth_distribution(df=synthData, id_num='190822a14')
    spf.plot_synth_distribution(df=synthData, id_num='190822a15')

    spf.plot_synth_distribution(df=synthData, id_num='190910a1')
    spf.plot_synth_distribution(df=synthData, id_num='190910a2')
    spf.plot_synth_distribution(df=synthData, id_num='190910a3')
    spf.plot_synth_distribution(df=synthData, id_num='190910a4')
    spf.plot_synth_distribution(df=synthData, id_num='190910a5')
    spf.plot_synth_distribution(df=synthData, id_num='190910a6')
    spf.plot_synth_distribution(df=synthData, id_num='190910a7')
    spf.plot_synth_distribution(df=synthData, id_num='190910a8')
    spf.plot_synth_distribution(df=synthData, id_num='190910a10')
    spf.plot_synth_distribution(df=synthData, id_num='190910a11')
    spf.plot_synth_distribution(df=synthData, id_num='190910a12')
    spf.plot_synth_distribution(df=synthData, id_num='190910a13')
