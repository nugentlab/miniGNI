# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: SSA Plot Functions
# Author: Chung Taing
# Date Updated: 10 April 2020
# Description: This script contains functions required to plot processed sample data. Sample data
# is processed by SSA Data Saver.
# =================================================================================================
# =================================================================================================
# =================================================================================================

# import packages
import colorcet as cc
import datetime as dt
import math
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import pandas as pd

from itertools import cycle
from matplotlib.dates import DateFormatter
from scipy import stats
from scipy.optimize import curve_fit
from lmfit.models import ExpressionModel

# define directories
miniGNI_dir = 'C:/Users/ntril/Dropbox/mini-GNI'
data_dir = miniGNI_dir + '/python_scripts/data'
plot_dir = miniGNI_dir + '/python_scripts/plots'

# =================================================================================================
# =================================================================================================
# =================================================================================================
# PLOT OPTIONS
# Function title: truncate_colormap
# Parameters: cmap, minval, maxval, n
# Description: This function truncates a colormap. This code was taken from Stack Overflow:
# https://stackoverflow.com/questions/18926031/how-to-extract-a-subset-of-a-colormap-as-a-new-colormap-in-matplotlib
# Section Description: This section sets plot options, such as colormap, font size, figure size, etc.
# =================================================================================================
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

# create truncated colormap to be used in plots
# it is truncated to remove the lighter colors, which show up poorly in print
cmap = truncate_colormap(cmap=plt.cm.inferno, minval=0, maxval=0.8)

# set the default size of plot
plt.rcParams['figure.figsize'] = (12.0, 9.0)

# set datetime axis format
myFmt = DateFormatter('%m/%d/%y')

# set font size for plots
plt.rcParams.update({'font.size': 24})

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: drop_samples
# Parameters: df, drop_list
# Description: This drops certain samples from the data frame. For some functions, it is better to
# observe only samples that had a proper humidity sensor. 
# =================================================================================================
def drop_samples(df, drop_list):
    for dropID in drop_list:
        df = df[df.id_number != dropID]
    return df

# these samples did not have direct relative humidity measurement due to lack of sensor
no_RH_list = ['181205a1', '181205a2', '181205a3', '181205a4', '181205a5', '181205a6', '181205a7', '181205a8', '190101a1', '190101a2', '190101a3', '190101a4', '190101a5', '190101a6', '190413a6', '190413a8', '190423a7', '190616a7', '190616a8']

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: roundup, rounddown
# Parameters: x, n
# Description: This rounds up or down the number x to the nearest (10^n)th place..
# =================================================================================================
def roundup(x, n):
    return int(math.ceil(x/(10**n)))*(10**n)
def rounddown(x, n):
    return int(math.floor(x/(10**n)))*(10**n)

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_all_samples
# Parameters: df, color_variable, color_label
# Description: This plots all the samples collected with date/time on the x-axis and sample mean
# # altitude on the y-axis. The scatter points are colored by a variable defined by color_variable. 
# # The color_label parameter is to label the colorbar.
# =================================================================================================
def plot_all_samples(df, color_variable, color_label):
    plt.rcParams['figure.figsize'] = (16.0, 9.0) # set figure size
    # setting colorbar minimum and maximum values
    norm = matplotlib.colors.Normalize(vmin=df[color_variable].min(), vmax=df[color_variable].max())
    fig, ax = plt.subplots()
    # scatter plotting all samples, colored by color_variable
    # # time on x-axis, altitude on y-axis
    ax.scatter(df.index, df.altitude, c=df[color_variable], cmap=cmap, s=200)
    # creating the colorbar
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
    plt.ylim(bottom=0, top=700) # set y-axis limits
    ax.xaxis.set_major_formatter(myFmt) # x-axis format
    ax.xaxis_date() # x-axis is date
    fig.autofmt_xdate() 
    ax.set_xlim([dt.date(2018, 12, 1), dt.date(2019, 10, 1)]) # set x-axis limits
    # labeling the axes and the colorbar
    plt.ylabel('Altitude (m)')
    plt.xlabel('Date (Month/Day/Year)')
    cb.set_label(color_label)
    plt.tight_layout() # tight layout
    plt.savefig(plot_dir + '/all_samples/samples_altitude_' + color_variable + '.pdf', format='pdf')
    #plt.savefig(plot_dir + '/all_samples/eps/samples_altitude_' + color_variable + '.eps', format='eps')
    #plt.savefig(plot_dir + '/all_samples/png/samples_altitude_' + color_variable + '.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_compare_woodcock
# Parameters: df, wdf1, wdf2, wdf3, wdf4, wdf5
# Description: This compares our data (df) to Woodcock's results (wdf1-5). This is the same as
# # plot_cumulative_concentration earlier, except it is expanded to include the Woodcock data.
# =================================================================================================
def plot_compare_woodcock(df, wdf1, wdf2, wdf3, wdf4, wdf5):
    plt.rcParams['figure.figsize'] = (11.0, 9.0) # plot size
    norm = matplotlib.colors.Normalize(vmin=df['surface_wind'].min(), vmax=df['surface_wind'].max())
    for row in df.itertuples():
        w = getattr(row, 'surface_wind')
        x = getattr(row, 'bin_middle')
        y = getattr(row, 'cutoff_cumu_conc')
        y = [count for item,count in zip(x,y) if item>=3.9]
        x = [item for item in x if item>=3.9]
        plt.plot(x, y, color=cmap(norm(w)), linewidth=2)
    # plotting the woodcock data
    plt.plot(wdf1.dry_radius, wdf1.n_concentration, label='1', color='grey', linestyle='--', linewidth=2)
    plt.plot(wdf2.dry_radius, wdf2.n_concentration, label='4', color='green', linestyle='--', linewidth=2)
    plt.plot(wdf3.dry_radius, wdf3.n_concentration, label='9', color='black', linestyle='--', linewidth=2)
    plt.plot(wdf4.dry_radius, wdf4.n_concentration, label='15', color='blue', linestyle='--', linewidth=2)
    plt.plot(wdf5.dry_radius, wdf5.n_concentration, label='35', color='purple', linestyle='--', linewidth=2)
    plt.yscale('log')
    # legend for the Woodcock data
    plt.legend(title='Woodcock Samples Wind Speed (m $\mathrm{s^{-1}}$)', bbox_to_anchor=(-0.1,1.05), loc='lower left', ncol=5)
    plt.xlim(left=0, right=16)
    plt.ylabel('Cumulative Number Concentration ($\mathrm{m^{-3}}$)')
    plt.xlabel('Dry Radius (\u03BCm)')
    plt.grid()
    cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm))
    cb.set_label('Wind Speed (m $\mathrm{s^{-1}}$)')
    plt.tight_layout()
    plt.savefig(plot_dir + '/cumulative_concentration/woodcock_comparison.pdf', format='pdf')
    #plt.savefig(plot_dir + '/cumulative_concentration/eps/woodcock_comparison.eps', format='eps')
    #plt.savefig(plot_dir + '/cumulative_concentration/png/woodcock_comparison.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_compare_woodcock_average
# Parameters: df, cutoff_winds
# Description: This compares our data (df) to Woodcock's results (wdf1-5). This is the same as
# # plot_cumulative_concentration earlier, except it is expanded to include the Woodcock data.
# =================================================================================================
def plot_compare_woodcock_average(df, wdf1, wdf2, wdf3, wdf4, wdf5, cutoff_winds, y_variable):
    plt.rcParams['figure.figsize'] = (16.0, 9.0)
    # set the values separating each altitude range for averaging
    # set colors
    colorcycler = cycle(['red','darkorange','darkgoldenrod','green','blue','purple', 'magenta', 'black'])
    # create figure
    fig, ax = plt.subplots()
    # plotting the woodcock data
    plt.plot(wdf1.dry_radius, wdf1.n_concentration, label='1 (Woodcock)', color='black', linestyle='--', linewidth=2)
    plt.plot(wdf2.dry_radius, wdf2.n_concentration, label='4 (Woodcock)', color='grey', linestyle='--', linewidth=2)
    plt.plot(wdf3.dry_radius, wdf3.n_concentration, label='9 (Woodcock)', color='saddlebrown', linestyle='--', linewidth=2)
    plt.plot(wdf4.dry_radius, wdf4.n_concentration, label='15 (Woodcock)', color='magenta', linestyle='--', linewidth=2)
    plt.plot(wdf5.dry_radius, wdf5.n_concentration, label='35 (Woodcock)', color='teal', linestyle='--', linewidth=2)
    # plot mean cumulative concentration
    for index, item in enumerate(cutoff_winds):
        if index == 0:
            continue
        last_item = cutoff_winds[index-1]
        tempdf = df[(df.surface_wind <= item) & (df.surface_wind > last_item)]
        temp_number = len(tempdf)
        temp_wind = tempdf.surface_wind.mean()
        temp_multiple_list = []
        for row in tempdf.itertuples():
            temp_list = getattr(row, y_variable)
            if len(temp_list) < 96:
                temp_list += [0] * (96-len(temp_list))
            temp_multiple_list.append(temp_list)
        temp_arrays = [np.array(item) for item in temp_multiple_list]
        y = [np.mean(item) for item in zip(*temp_arrays)]
        x = df['bin_middle'].iloc[0]
        y = [count for item,count in zip(x,y) if item>=3.9]
        x = [item for item in x if item>=3.9]
        #plt.plot(x, y, label=str(int(temp_wind)) + ', N=' + str(temp_number), linewidth=2, color=next(colorcycler))
        plt.plot(x, y, label=str(round(last_item, 1)) + '-' + str(round(item, 1)) + ', N=' + str(temp_number), linewidth=3, color=next(colorcycler))
    plt.yscale('log') # log scale on y-axis
    #plt.ylim(bottom=0.1, top=1000000) # limits on the y-axis
    plt.xlim(left=0, right=16) # limits on the x-axis
    plt.ylabel('Cumulative Number Concentration ($\mathrm{m^{-3}}$)') # label on y-axis
    plt.xlabel('Dry Radius (\u03BCm)') # label on x-axis
    plt.grid() # gridded plot
    # legend for average wind samples
    lgd = plt.legend(bbox_to_anchor=(1.0,1.0), loc='upper left', ncol=1, fontsize=24, title = 'Surface Wind, Sample Size')
    #cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm)) # create colorbar
    #cb.set_label(color_label) # colorbar label
    plt.tight_layout()
    #plt.show()
    plt.savefig(plot_dir + '/cumulative_concentration/' + y_variable + '_mean_woodcock_comparison.pdf', format='pdf')
    #plt.savefig(plot_dir + '/cumulative_concentration/eps/mean_cumulative_concentration_by_phngwind.eps', format='eps')
    #plt.savefig(plot_dir + '/cumulative_concentration/png/mean_cumulative_concentration_by_phngwind.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_correlation
# Parameters: df, x_variable, y_variable, x_label, y_label
# Description: This creates a scatter plot and fits a line to the data, giving you the rsquared
# # value. Can be used to quickly plot and see correlation between 2 variables of choice.
# =================================================================================================
def plot_correlation(df, x_variable, y_variable, x_label, y_label):
    plt.rcParams['figure.figsize'] = (12.0, 9.0)
    # if RH is a chosen variable, drop the samples with estimated RH
    if x_variable=='rh':
        df = dropSlides(df, dropList=noRH)
    if y_variable=='rh':
        df = dropSlides(df, dropList=noRH)
    x = df[x_variable]
    y = df[y_variable]
    # plot and R-squared analysis
    plt.scatter(x, y, s=500)
    z = np.polyfit(x, y, 1) # fit data to line
    p = np.poly1d(z)
    yfit = p(x)
    plt.plot(x, yfit, linewidth=2, color='red') # plot the fitted line
    ybar = np.sum(y)/len(y)
    ssres = np.sum((y-yfit)**2)
    sstot = np.sum((y-ybar)**2)
    rsquared = 1 - ssres/sstot # rsquared value is calculcated
    # annotate the fitted line equation and the rsquared value
    plt.annotate('y=%.1fx+%.1f'%(z[0],z[1]), xy=(min(x), max(y) - (max(y)-min(y))/4), size=24)
    plt.annotate('$r^2$=%.2f'%(rsquared), xy=(min(x), max(y) - (max(y)-min(y))/3), size=24)
    plt.xlabel(x_label) # label x-axis
    plt.ylabel(y_label) # label y-axis
    plt.grid() # give the plot a grid
    plt.tight_layout()
    plt.savefig(plot_dir + '/correlation/' + x_variable + '_correlation_' + y_variable + '.pdf', format='pdf')
    #plt.savefig(plot_dir + '/correlation/eps/' + x_variable + '_correlation_' + y_variable + '.eps', format='eps')
    #plt.savefig(plot_dir + '/correlation/png/' + x_variable + '_correlation_' + y_variable + '.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_cumulative_concentration
# Parameters: df, color_variable, color_label
# Description: This creates a plot of the cumulative concentration of the size distribution of all
# # samples. The meaning of cumulative concentration is that at each bin of the size distribution, 
# # the concentration of all bins larger than that bin is plotted. Each line of cumulative
# # concentration represents one sample, and they are colored by a variable of choice. Note that
# # the cutoff cumulative concentration (cutoff_cumu_conc) is used here. This means that all the
# # samples are cut off at the same point for comparison purposes. The cutoff is 3.9 microns.
# =================================================================================================
def plot_cumulative_concentration(df, color_variable, color_label):
    plt.rcParams['figure.figsize'] = (12.0, 9.0)
    # set minimum and maximum of colorbar
    norm = matplotlib.colors.Normalize(vmin=df[color_variable].min(), vmax=df[color_variable].max())
    for row in df.itertuples(): # walk through the samples data frame
        w = getattr(row, color_variable) # pull the variable that you want to use for color
        x = getattr(row, 'bin_middle')
        y = getattr(row, 'cutoff_cumu_conc') # cutoff cumulative concentration or cutoff cumulative salt
        # plot the cumulative concentration size distribution for each sample
        plt.plot(x, y, label=w, color=cmap(norm(w)), linewidth=2)
    plt.yscale('log') # log scale on y-axis
    plt.ylim(bottom=0.1, top=100000) # limits on the y-axis
    plt.xlim(left=3, right=16) # limits on the x-axis
    plt.ylabel('Cumulative Number Concentration ($\mathrm{m^{-3}}$)') # label on y-axis
    plt.xlabel('Dry Radius (\u03BCm)') # label on x-axis
    plt.grid() # gridded plot
    cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm)) # create colorbar
    cb.set_label(color_label) # colorbar label
    plt.tight_layout()
    plt.savefig(plot_dir + '/cumulative_concentration/cumulative_concentration_by_' + color_variable + '.pdf', format='pdf')
    #plt.savefig(plot_dir + '/cumulative_concentration/eps/cumulative_concentration_by_' + color_variable + '.eps', format='eps')
    #plt.savefig(plot_dir + '/cumulative_concentration/png/cumulative_concentration_by_' + color_variable + '.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_average_cumulative_concentration_altitude
# Parameters: df, cutoff_altitudes
# Description: This creates a plot of the cumulative concentration of the size distribution of all
# # samples. The meaning of cumulative concentration is that at each bin of the size distribution, 
# # the concentration of all bins larger than that bin is plotted. Each line of cumulative
# # concentration represents an average sample at altitude (0-99 m, 100-199 m, etc), and they are 
# # colored by a variable of choice. Note that the cutoff cumulative concentration  is used here. 
# # This means that all the samples are cut off at the same point for comparison purposes. 
# # The cutoff is 3.9 microns.
# =================================================================================================
def plot_cumulative_concentration_average(df, color_variable, cutoff_list, color_label):
    plt.rcParams['figure.figsize'] = (16.0, 9.0)
    # set colors
    colorcycler = cycle(['red','darkorange','darkgoldenrod','green','blue','purple', 'magenta', 'black'])
    fig, ax = plt.subplots()
    for index, item in enumerate(cutoff_list):
        if index == 0:
            continue
        last_item = cutoff_list[index-1]
        tempdf = df[(df[color_variable] <= item) & (df[color_variable] > last_item)]
        sample_size = len(tempdf)
        if color_variable == 'altitude':
            min_value = int(tempdf[color_variable].min())
            max_value = int(tempdf[color_variable].max())
        else:
            min_value = round(tempdf[color_variable].min(), 2)
            max_value = round(tempdf[color_variable].max(), 2)
        temp_multiple_list = []
        for row in tempdf.itertuples():
            temp_list = getattr(row, 'cutoff_cumu_conc')
            if len(temp_list) < 96:
                temp_list += [0] * (96-len(temp_list))
            temp_multiple_list.append(temp_list)
        temp_arrays = [np.array(item) for item in temp_multiple_list]
        y = [np.mean(item) for item in zip(*temp_arrays)]
        # =========================================================================================
        # find lower and upper bounds of 95% confidence interval (1.96 times standard error)
        lb = [np.mean(item) - 1.96*stats.sem(item) for item in zip(*temp_arrays)]
        ub = [np.mean(item) + 1.96*stats.sem(item) for item in zip(*temp_arrays)]
        # find lower and upper bounds using standard deviation instead
        #lb = [np.mean(item) - np.std(item) for item in zip(*temp_arrays)]
        #ub = [np.mean(item) + np.std(item) for item in zip(*temp_arrays)]
        # find lower and upper bounds using min and max instead
        #lb = [np.min(item) for item in zip(*temp_arrays)]
        #ub = [np.max(item) for item in zip(*temp_arrays)]
        # =========================================================================================
        x = df['bin_middle'].iloc[0]
        color_choice = next(colorcycler)
        plt.plot(x, y, label=str(min_value) + '-' + str(max_value) + ', N=' + str(sample_size), linewidth=3, color=color_choice)
        # show the 95% confidence interval (1.96 times the standard error se)
        if index==1 or index==(len(cutoff_list)-1):
            ax.fill_between(x, lb, ub, color=color_choice, alpha=0.1)
    plt.yscale('log') # log scale on y-axis
    plt.ylim(bottom=0.1, top=10000) # limits on the y-axis
    plt.xlim(left=3, right=16) # limits on the x-axis
    plt.ylabel('Cumulative Number Concentration ($\mathrm{m^{-3}}$)') # label on y-axis
    plt.xlabel('Dry Radius (\u03BCm)') # label on x-axis
    plt.grid() # gridded plot
    lgd = plt.legend(bbox_to_anchor=(1.0,1.0), loc='upper left', ncol=1, fontsize=24, title = color_label + ', Sample Size')
    plt.tight_layout()
    #plt.show()
    plt.savefig(plot_dir + '/cumulative_concentration/mean_cumulative_concentration_by_' + color_variable + '.pdf', format='pdf')
    #plt.savefig(plot_dir + '/cumulative_concentration/eps/mean_cumulative_concentration_by_altitude.eps', format='eps')
    #plt.savefig(plot_dir + '/cumulative_concentration/png/mean_cumulative_concentration_by_altitude.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_lognormal_stats
# Parameters: df
# Description: This creates histograms showing the distribution of total salt mass, mu, and sigma
# # for all the samples. Mu and sigma refer to the geometric mean and geometric standard deviation
# # of the lognormal distribution fitted to each sample.
# =================================================================================================
def plot_lognormal_stats(df, df2):
    plt.rcParams['figure.figsize'] = (12.0, 9.0)
    df2 = df2[df2.altitude<650]
    mu = df['muG'] # geometric mean for each sample
    sigma = df['sigmaG'] # geometric standard deviation for each sample
    salt = df['cutoff_total_mass'] # total salt mass for each sample
    rchi = df['chi2'] # reduced chi square
    mu_v = df2['muG'] # geometric mean for each VOCALS sample
    print(mu_v)
    sigma_v = df2['sigmaG'] # geometric standard deviation for each VOCALS sample
    salt_v = df2['cutoff_total_mass'] # total salt mass for each VOCALs sample
    rchi_v = df2['chi2'] # reduced chi square for each VOCALS sample
    n1 = len(df) # sample size of Oahu sampling
    n2 = len(df2) # sample size of VOCALS sampling
    # mu histogram
    bins_list = np.linspace(0, 4.5, 31) # creates the histogram bins
    plt.hist(mu, bins=bins_list, label='Oahu', facecolor='red', edgecolor='black', alpha=0.5, weights=np.ones(n1)/n1)
    plt.hist(mu_v, bins=bins_list, label='VOCALS', facecolor='blue', edgecolor='black', alpha=0.5, weights=np.ones(n2)/n2)
    plt.ylabel('Relative Frequency') # label the y-axis
    plt.xlabel('$r_g$ (\u03BCm)') # label the x-axis
    plt.tight_layout()
    plt.legend()
    plt.savefig(plot_dir + '/lognormal_stats/mu_distribution.pdf', format='pdf')
    #plt.savefig(plot_dir + '/lognormal_stats/eps/mu_distribution.eps', format='eps')
    #plt.savefig(plot_dir + '/lognormal_stats/png/mu_distribution.png', format='png')
    plt.close('all') # closes plots to create the next one
    # sigma histogram
    bins_list = np.linspace(1,6,26)
    plt.hist(sigma, bins=bins_list, label='Oahu', facecolor='red', edgecolor='black', alpha=0.5, weights=np.ones(n1)/n1)
    plt.hist(sigma_v, bins=bins_list, label='VOCALS', facecolor='blue', edgecolor='black', alpha=0.5, weights=np.ones(n2)/n2)
    plt.ylabel('Relative Frequency')
    plt.xlabel('$\u03C3_g$ (\u03BCm)')
    plt.tight_layout()
    plt.legend()
    plt.savefig(plot_dir + '/lognormal_stats/sigma_distribution.pdf', format='pdf')
    #plt.savefig(plot_dir + '/lognormal_stats/eps/sigma_distribution.eps', format='eps')
    #plt.savefig(plot_dir + '/lognormal_stats/png/sigma_distribution.png', format='png')
    plt.close('all')
    # salt mass histogram
    bins_list = np.linspace(0,20.0,26)
    plt.hist(salt, bins=bins_list, label='Oahu', facecolor='red', edgecolor='black', alpha=0.5, weights=np.ones(n1)/n1)
    plt.hist(salt_v, bins=bins_list, label='VOCALS', facecolor='blue', edgecolor='black', alpha=0.5, weights=np.ones(n2)/n2)
    plt.ylabel('Relative Frequency')
    plt.xlabel('Salt Mass (\u03BCg $\mathrm{m^{-3}}$)')
    plt.tight_layout()
    plt.legend()
    plt.savefig(plot_dir + '/lognormal_stats/mass_distribution.pdf', format='pdf')
    #plt.savefig(plot_dir + '/lognormal_stats/eps/mass_distribution.eps', format='eps')
    #plt.savefig(plot_dir + '/lognormal_stats/png/mass_distribution.png', format='png')
    plt.close('all')
    # salt mass histogram
    bins_list = np.linspace(0,300,31)
    plt.hist(rchi, bins=bins_list, label='Oahu', facecolor='red', edgecolor='black', alpha=0.5, weights=np.ones(n1)/n1)
    plt.hist(rchi_v, bins=bins_list, label='VOCALS', facecolor='blue', edgecolor='black', alpha=0.5, weights=np.ones(n2)/n2)
    plt.ylabel('Relative Frequency')
    plt.xlabel('Reduced Chi-Square')
    plt.tight_layout()
    plt.legend()
    plt.savefig(plot_dir + '/lognormal_stats/rchi_distribution.pdf', format='pdf')
    #plt.savefig(plot_dir + '/lognormal_stats/eps/rchi_distribution.eps', format='eps')
    #plt.savefig(plot_dir + '/lognormal_stats/png/rchi_distribution.png', format='png')
    plt.close('all')

def plot_lognormal_comparison(df):
    # mean
    plt.scatter(x=df.muG, y=df.gni_mug)
    plt.plot(df.muG, df.muG, color='red', linewidth=2)
    plt.ylabel('Jorgen')
    plt.xlabel('Aaron')
    plt.title('Geometric Mean Calculation Comparison')
    plt.savefig(plot_dir + '/lognormal_stats/mu_comparison.pdf', format='pdf')
    #plt.savefig(plot_dir + '/lognormal_stats/eps/mu_comparison.eps', format='eps')
    #plt.savefig(plot_dir + '/lognormal_stats/png/mu_comparison.png', format='png')
    plt.close('all')
    # standard deviation
    plt.scatter(x=df.sigmaG, y=df.gni_std)
    plt.plot(df.sigmaG, df.sigmaG, color='red', linewidth=2)
    plt.ylabel('Jorgen')
    plt.ylim(bottom=0, top=5)
    plt.xlim(left=0, right=5)
    plt.xlabel('Aaron')
    plt.title('Geometric St. Dev. Calculation Comparison')
    plt.savefig(plot_dir + '/lognormal_stats/std_comparison.pdf', format='pdf')
    #plt.savefig(plot_dir + '/lognormal_stats/eps/std_comparison.eps', format='eps')
    #plt.savefig(plot_dir + '/lognormal_stats/png/std_comparison.png', format='png')
    plt.close('all')
    # chi square
    plt.scatter(x=df.chi2, y=df.gni_chi)
    plt.plot(df.chi2, df.chi2, color='red', linewidth=2)
    plt.ylabel('Jorgen')
    plt.xlabel('Aaron')
    plt.ylim(bottom=0, top=250)
    plt.xlim(left=0, right=250)
    plt.title('Chi-Square Calculation Comparison')
    plt.savefig(plot_dir + '/lognormal_stats/chi_comparison.pdf', format='pdf')
    #plt.savefig(plot_dir + '/lognormal_stats/eps/chi_comparison.eps', format='eps')
    #plt.savefig(plot_dir + '/lognormal_stats/png/chi_comparison.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_mass_distribution_tenpercent
# Parameters: df
# Description: 
# =================================================================================================
def plot_mass_distribution_tenpercent(df):
    plt.rcParams['figure.figsize'] = (16.0, 9.0)
    # set the values separating each altitude range for averaging
    salt_list = df['cutoff_total_mass'].sort_values()
    cutoff_salts = [salt_list[i] for i in range(0, len(salt_list), 10)]
    # set colors
    colorcycler = cycle(['red','darkorange','darkgoldenrod','green','blue','purple', 'magenta', 'black'])
    linecycler = cycle(['-','--',':'])
    fig, ax = plt.subplots()
    for index, item in enumerate(cutoff_salts):
        if index == 0:
            continue
        last_item = cutoff_salts[index-1]
        tempdf = df[(df.cutoff_total_mass < item) & (df.cutoff_total_mass >= last_item)]
        mean_salt = round(tempdf.cutoff_total_mass.mean(), 2)
        sample_size = len(tempdf)
        #min_salt = int(tempdf.altitude.min())
        #max_salt = int(tempdf.altitude.max())
        x = df['bin_middle'].iloc[0]
        temp_multiple_list = []
        for row in tempdf.itertuples():
            temp_list = getattr(row, 'bin_cutoff_salt')
            if len(temp_list) < 96:
                temp_list += [0] * (96-len(temp_list))
            temp_list = [item for item,size in zip(temp_list,x) if size>3.8]
            temp_multiple_list.append(temp_list)
        temp_arrays = [np.array(item) for item in temp_multiple_list]
        x = [item for item in x if item>3.8]
        y = [np.mean(item)/0.2 for item in zip(*temp_arrays)]
        # =========================================================================================
        # find lower and upper bounds of 95% confidence interval (1.96 times standard error)
    #    lb = [np.mean(item) - 1.96*stats.sem(item) for item in zip(*temp_arrays)]
    #    ub = [np.mean(item) + 1.96*stats.sem(item) for item in zip(*temp_arrays)]
        # find lower and upper bounds using standard deviation instead
        #lb = [np.mean(item) - np.std(item) for item in zip(*temp_arrays)]
        #ub = [np.mean(item) + np.std(item) for item in zip(*temp_arrays)]
        # find lower and upper bounds using min and max instead
        #lb = [np.min(item) for item in zip(*temp_arrays)]
        #ub = [np.max(item) for item in zip(*temp_arrays)]
        # =========================================================================================
        color_choice = next(colorcycler)
        #plt.plot(x, y, label=str(min_alt) + '-' + str(max_alt) + ', N=' + str(sample_size), linewidth=3, color=color_choice)
        plt.plot(x, y, label=str(mean_salt), linewidth=3, color=color_choice, linestyle=next(linecycler))
        # show the 95% confidence interval (1.96 times the standard error se)
    #    if index==1 or index==8:
    #        ax.fill_between(x, lb, ub, color=color_choice, alpha=0.1)
    #plt.yscale('log') # log scale on y-axis
    plt.xscale('log') # log scale on x-axis
    #plt.ylim(bottom=0.1, top=10000) # limits on the y-axis
    plt.xlim(left=3.5, right=16) # limits on the x-axis
    plt.ylabel('Mass Concentration (\u03BCg $\mathrm{m^{-3}}$ \u03BC$\mathrm{m^{-1}}$)') # label on y-axis
    plt.xlabel('Dry Radius (\u03BCm)') # label on x-axis
    plt.grid() # gridded plot
    #ldg = plt.legend(title='Mean Sample Total Mass')
    lgd = plt.legend(bbox_to_anchor=(1.0,1.0), loc='upper left', ncol=1, fontsize=24, title = 'Mean Sample Mass')
    plt.tight_layout()
    #plt.show()
    plt.savefig(plot_dir + '/all_samples/mean_mass_distribution_tenpercent.pdf', format='pdf')
    #plt.savefig(plot_dir + '/mean_mass_distribution_tenpercent.eps', format='eps')
    #plt.savefig(plot_dir + '/mean_mass_distribution_tenpercent.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_ranz_wong
# Parameters: df, plot_resolution, max_radius, max_wind_speed
# Description: This creates a contour plot of collision efficiency's relationship with
# # SSA dry radius and wind speed. The plot can be altered to show a range of dry radius and
# # wind speeds. The resolution can be changed as well. The default is 100. Warning: having a high
# # resolution will lead to longer computation times.
# =================================================================================================
def plot_ranz_wong(plot_resolution, max_radius, max_wind_speed):
    # setting variables for tricontour plot
    res = plot_resolution # just shortening the variable name
    dry_radius_list = [(x/1000000)/res for x in range(1*res, max_radius*res + 1)]
    air_speed_list = [y/res for y in range(1*res, max_wind_speed*res + 1)]
    # I want to calculate the collision efficiency for each pair of dry_radius and air_speed
    # # values. So I will repeat each item in dry_radius a number of time equal to the number of 
    # # objects in air_speed. Then, I will repeat the air_speed list a number of times equal to
    # # the length of the dry_radius list. By doing this, I can iterate over both lists to 
    # # calculcate collision efficiency for each pairing of dry radius and wind speed.
    ssa_dry_radius = [item for item in dry_radius_list for i in range(len(air_speed_list))]
    wind_speed = air_speed_list*len(dry_radius_list)
    ce_list = []
    for x, y in zip(ssa_dry_radius, wind_speed):
        ranzwong.append(rw.get_collision_efficiency(pressure=99053.14, temperature=297.55, air_speed=y, rh=0.7492, dry_radius=x))
    # set size of plot
    plt.rcParams['figure.figsize'] = (12.0, 8.0)
    # defining x, y, z for tricontour style
    x = [1000000*item for item in ssa_dry_radius]
    y = wind_speed
    z = ce_list
    # defining levels for color and line contours
    color_levels = np.arange(0, 1.01, 0.01)
    line_levels = [0.01, 0.05, 0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
    triang = tri.Triangulation(x, y)
    cs = plt.tricontour(triang, z, linewidths=1, levels=line_levels, colors='k')
    tcf = plt.tricontourf(triang, z, levels=color_levels, cmap=cmap)
    plt.clabel(cs, inline=1, fontsize=24) # labeling the line contours
    # creating colorbar
    cb = plt.colorbar(tcf)
    cb.set_label('Collision Efficiency') # colorbar title
    ticks = np.around(np.arange(0.0, 1.1, 0.1), decimals=1)
    plt.clim(0, 1)
    cb.set_ticks(ticks) # colorbar ticks
    cb.set_ticklabels(ticks) # colorbar tick labels
    # axis ticks
    plt.xlim(left=1, right=maxRadius)
    plt.ylim(bottom=1, top=maxWindSpeed)
    plt.xticks(range(1, maxRadius+1, 1))
    plt.yticks(range(1, maxWindSpeed+1, 1))
    # axes labels
    plt.ylabel('Wind Speed (m $\mathrm{s^{-1}}$)')
    plt.xlabel('Dry Radius (\u03BCm)')
    plt.savefig('plots/collision_efficiency/ce_' + str(max_radius) + '_radius_' + str(max_wind_speed) + '_wind.pdf', format='pdf')
    #plt.savefig('plots/collision_efficiency/png/ce_' + str(max_radius) + '_radius_' + str(max_wind_speed) + '_wind.png')
    #plt.savefig('plots/collision_efficiency/eps/ce_' + str(max_radius) + '_radius_' + str(max_wind_speed) + '_wind.eps')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_concentration_altitude
# Parameters: df, sample_date
# Description: This creates cumulative concentration plots as described by 
# # plot_cumulative_concentration above, but this time only for each sample day. It shows the 
# # cumulative concentration for each sample on one sample day, with each line of cumulative
# # concentration colored by altitude. These plots are also labeled by average surface wind and
# # average buoy wave height for that sample day.
# =================================================================================================
def plot_sample_day_concentration(df, sample_date):
    plt.rcParams['figure.figsize'] = (12.0, 9.0) # figure size
    # getting only samples associated with sample_date
    df = df.loc[df['id_number'].str.contains(sample_date)]
    # choose bottom and top values of colorbar
    norm = matplotlib.colors.Normalize(vmin=rounddown(df['altitude'].min(), 1), vmax=roundup(df['altitude'].max(), 1))
    average_wind = round(df.surface_wind.mean(), 1) # average wind
    average_wave = round(df.wave_height.mean(), 1) # average wave height
    for row in df.itertuples(): # walk through the samples
        c = getattr(row, 'altitude') # color by altitude
        x = getattr(row, 'bin_middle') # x-axis bin size
        y = getattr(row, 'cutoff_cumu_conc') # y-axis cumulative concentration
        plt.plot(x, y, label=c, color=cmap(norm(c)), linewidth=2)
    plt.yscale('log') # log scale for y-axis
    plt.ylim(bottom=0.1, top=100000) # limits of y-axis
    plt.xlim(left=3, right=16) # limits of x-axis
    plt.xlabel('Bin Dry Radius (\u03BCm)') # x-axis label
    plt.ylabel('Number Concentration ($\mathrm{m^{-3}}$)') # y-axis label
    plt.grid() # gridded plot
    # creating annotations using the average wind and wave height
    plt.annotate('Mean Surface Wind = %.1f m/s'%(average_wind), xy=(4, 20000), size=24)
    plt.annotate('Mean Significant Wave Height = %.1f m'%(average_wave), xy=(4, 50000), size=24)
    # create color bar and label it
    cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm))
    cb.set_label('Altitude (m)')
    # title the plot, give it a tight layout, and save it
    plt.title('Sample Date ' + sample_date)
    plt.tight_layout()
    plt.savefig(plot_dir + '/sample_day/cumulative_by_altitude_' + sample_date + '.pdf', format='pdf')
    #plt.savefig(plot_dir + '/sample_day/eps/cumulative_by_altitude_' + sample_date + '.eps', format='eps')
    #plt.savefig(plot_dir + '/sample_day/png/cumulative_by_altitude_' + sample_date + '.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_average_cumulative_concentration_altitude
# Parameters: df, cutoff_altitudes
# Description: This creates a plot of the cumulative concentration of the size distribution of all
# # samples. The meaning of cumulative concentration is that at each bin of the size distribution, 
# # the concentration of all bins larger than that bin is plotted. Each line of cumulative
# # concentration represents an average sample at altitude (0-99 m, 100-199 m, etc), and they are 
# # colored by a variable of choice. Note that the cutoff cumulative concentration  is used here. 
# # This means that all the samples are cut off at the same point for comparison purposes. 
# # The cutoff is 3.9 microns.
# =================================================================================================
def plot_sample_day_concentration_average(df, sample_date):
    plt.rcParams['figure.figsize'] = (16.0, 9.0)
    # getting only samples associated with sample_date
    tempdf = df.loc[df['id_number'].str.contains(sample_date)]
    # find separating altitudes
    sorted_altitude = tempdf.altitude.sort_values()
    diff_list = sorted_altitude.diff().fillna(0)
    cutoff_diff = 1.5*diff_list.mean()
    diff_list = sorted_altitude.diff().fillna(500)
    cutoff_altitudes = [item for item, value in zip(sorted_altitude, diff_list) if value>cutoff_diff]
    cutoff_altitudes.append(1000)
    # set colors
    colorcycler = cycle(['red','green','blue','purple','black','darkorange','darkgoldenrod','magenta'])
    fig, ax = plt.subplots()
    for index, item in enumerate(cutoff_altitudes):
        if index == 0:
            continue
        last_item = cutoff_altitudes[index-1]
        tempdf2 = tempdf[(tempdf.altitude < item) & (tempdf.altitude >= last_item)]
        sample_size = len(tempdf2)
        min_alt = int(tempdf2.altitude.min())
        max_alt = int(tempdf2.altitude.max())
        temp_multiple_list = []
        for row in tempdf2.itertuples():
            temp_list = getattr(row, 'cutoff_cumu_conc')
            if len(temp_list) < 96:
                temp_list += [0] * (96-len(temp_list))
            temp_multiple_list.append(temp_list)
        temp_arrays = [np.array(item) for item in temp_multiple_list]
        y = [np.mean(item) for item in zip(*temp_arrays)]
        rsd = [stats.sem(item)*100/np.mean(item) for item in zip(*temp_arrays)]
        # =========================================================================================
        # find lower and upper bounds of 95% confidence interval (1.96 times standard error)
        #lb = [np.mean(item) - 1.96*stats.sem(item) for item in zip(*temp_arrays)]
        #ub = [np.mean(item) + 1.96*stats.sem(item) for item in zip(*temp_arrays)]
        
        # find lower and upper bounds using standard deviation instead
        #lb = [np.mean(item) - np.std(item) for item in zip(*temp_arrays)]
        #ub = [np.mean(item) + np.std(item) for item in zip(*temp_arrays)]
        
        # find lower and upper bounds using min and max instead
        lb = [np.min(item) for item in zip(*temp_arrays)]
        ub = [np.max(item) for item in zip(*temp_arrays)]
        # =========================================================================================
        x = df['bin_middle'].iloc[0]
        color_choice = next(colorcycler)
        plt.plot(x, y, label=str(min_alt) + '-' + str(max_alt) + ', N=' + str(sample_size), linewidth=2, color=color_choice)
        ax.fill_between(x, lb, ub, color=color_choice, alpha=0.1)
        # show the 95% confidence interval (1.96 times the standard error se)
    #    if index==1 or index==8:
    #        ax.fill_between(x, lb, ub, color=color_choice, alpha=0.1)
    plt.yscale('log') # log scale on y-axis
    plt.ylim(bottom=0.1, top=10000) # limits on the y-axis
    plt.xlim(left=3, right=16) # limits on the x-axis
    plt.ylabel('Cumulative Number Concentration ($\mathrm{m^{-3}}$)') # label on y-axis
    plt.xlabel('Dry Radius (\u03BCm)') # label on x-axis
    plt.grid() # gridded plot
    lgd = plt.legend(bbox_to_anchor=(1.0,1.0), loc='upper left', ncol=1, fontsize=24, title = 'Altitude (m), Sample Size \n Sample Date: ' + sample_date)
    plt.tight_layout()
    #plt.show()
    plt.savefig(plot_dir + '/sample_day/mean_cumulative_by_altitude_' + sample_date + '.pdf', format='pdf')
    #plt.savefig(plot_dir + '/sample_day/eps/mean_cumulative_by_altitude_' + sample_date + '.eps', format='eps')
    #plt.savefig(plot_dir + '/sample_day/png/mean_cumulative_by_altitude_' + sample_date + '.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_size_distribution
# Parameters: df, id_num
# Description: This creates a histogram representing the size distribution for a particular sample.
# # The size distribution is a number concentration per bin, with each bin having a bin width of 
# # 0.2 microns (e.g. 4.7-4.9 um). The size distributions are fitted to lognormal distributions.
# # The average altitude, surface wind speed, and buoy wave height for each sample is annotated.
# # Lognormal fit parameters are also annotated: geometric mean, geometric standard deviation,
# # chi squared value, and p-value.
# =================================================================================================
def plot_size_distribution(df, id_num):
    fig, ax = plt.subplots()
    plt.rcParams['figure.figsize'] = (12.0, 9.0) # plot size
    x = df.loc[df['id_number'] == id_num, 'bin_middle'].values[0] # bins
    y = df.loc[df['id_number'] == id_num, 'bin_real_conc'].values[0] # number concentration
    # get the nonempty bins
    x_nonempty = np.array([item for item,count in zip(x,y) if count>0])
    y_nonempty = np.array([count for count in y if count>0])
    # label the axes and set y-axis limit
    plt.ylabel('Number Concentration ($\mathrm{m^{-3}}$)')
    plt.ylim(bottom=0.1, top=1000000)
    # get altitude, surface wind, and buoy wave height values
    #altitude_label = df.loc[df['id_number'] == id_num, 'altitude'].values[0]
    #wind_label = df.loc[df['id_number'] == id_num, 'surface_wind'].values[0]
    #wave_label = df.loc[df['id_number'] == id_num, 'wave_height'].values[0]
    # plot the size distribution
    plt.bar(x=x, height=y, width=0.2)
    # =============================================================================================
    # LOGNORMAL DISTRIBUTION FIT ==================================================================
    # =============================================================================================
    # read in lognormal fit parameters
    area = df.loc[df['id_number'] == id_num, 'lognorm_area'].values[0]
    mu_g = df.loc[df['id_number'] == id_num, 'muG'].values[0]
    sigma_g = df.loc[df['id_number'] == id_num, 'sigmaG'].values[0]
    chi2 = df.loc[df['id_number'] == id_num, 'chi2'].values[0]
    #p = df.loc[df['id_number'] == id_num, 'p_value'].values[0]
    mu = math.log(mu_g) # arithmetic mean is log of geometric mean for lognormal distribution
    sigma = math.log(sigma_g) # standard deviation relationship with geometric standard deviation
    # putting the lognormal parameters in to plot the lognormal distribution
    x_lognorm, y_lognorm = x_nonempty, area*(1/(x_nonempty*sigma*math.sqrt(2*math.pi)))*np.exp((-np.power(np.log(x_nonempty)-mu, 2))/(2*np.power(sigma, 2)))
    # plotting the lognormal fit line
    plt.plot(x_lognorm, y_lognorm, 'r-')
    plt.yscale('log') # log scale for y-axis
    plt.xlim(left=0, right=16) # limits on x-axis
    plt.xlabel('Bin Dry Radius (\u03BCm)') # label on x-axis
    plt.grid() # gridded plot
    plt.title('Sample ' + id_num) # title shows which sample it is
    # creating annotations for geometric mean, geometric standard deviation, chi-squared value,
    # # p-value, sample surface wind, sample buoy wave height, and sample altitude
    plt.annotate('$\u03BC_g$ = %.3f \u03BCm'%(mu_g), xy=(10,630957), size=24, verticalalignment='center')
    plt.annotate('$\u03C3_g$ = %.3f'%(sigma_g), xy=(10,316228), size=24, verticalalignment='center')
    plt.annotate('Reduced $\u03A7^2$ = %.1f'%(chi2), xy=(10,158489), size=24, verticalalignment='center')
    #plt.annotate('$p$ = %.3f'%(p), xy=(12,15000), size=24)
    #plt.annotate('Surface Wind = %.1f m $\mathrm{s^{-1}}$'%(wind_label), xy=(6, 1500), size=24)
    #plt.annotate('Significant Wave Height = %.1f m'%(wave_label), xy=(6, 3000), size=24)
    #plt.annotate('Altitude = %.1f m'%(altitude_label), xy=(6, 6000), size=24)
    plt.tight_layout()
    #ax.set_rasterized(True)
    plt.savefig(plot_dir + '/histogram/histogram_' + id_num + '.png', format='png')
    #plt.savefig(plot_dir + '/histogram/png/histogram_' + id_num + '.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_size_distribution
# Parameters: df, id_num
# Description: This creates a histogram representing the size distribution for a particular sample.
# # The size distribution is a number concentration per bin, with each bin having a bin width of 
# # 0.2 microns (e.g. 4.7-4.9 um). The size distributions are fitted to lognormal distributions.
# # The average altitude, surface wind speed, and buoy wave height for each sample is annotated.
# # Lognormal fit parameters are also annotated: geometric mean, geometric standard deviation,
# # chi squared value, and p-value.
# =================================================================================================
def plot_synth_distribution(df, id_num):
    fig, ax = plt.subplots()
    plt.rcParams['figure.figsize'] = (12.0, 9.0) # plot size
    x = df.loc[df['id_number'] == id_num, 'bin_middle'].values[0] # bins
    y = df.loc[df['id_number'] == id_num, 'synth_conc'].values[0] # number concentration
    # get the nonempty bins
    x_nonempty = np.array([item for item,count in zip(x,y) if count>0])
    y_nonempty = np.array([count for count in y if count>0])
    # label the axes and set y-axis limit
    plt.ylabel('Number Concentration ($\mathrm{m^{-3}}$)')
    plt.ylim(bottom=0.1, top=1000000)
    # get altitude, surface wind, and buoy wave height values
    #altitude_label = df.loc[df['id_number'] == id_num, 'altitude'].values[0]
    #wind_label = df.loc[df['id_number'] == id_num, 'surface_wind'].values[0]
    #wave_label = df.loc[df['id_number'] == id_num, 'wave_height'].values[0]
    # plot the size distribution
    plt.bar(x=x, height=y, width=0.2)
    # =============================================================================================
    # LOGNORMAL DISTRIBUTION FIT ==================================================================
    # =============================================================================================
    # read in lognormal fit parameters
    area = df.loc[df['id_number'] == id_num, 'lognorm_area'].values[0]
    mu_g = df.loc[df['id_number'] == id_num, 'muG'].values[0]
    sigma_g = df.loc[df['id_number'] == id_num, 'sigmaG'].values[0]
    chi2 = df.loc[df['id_number'] == id_num, 'chi2'].values[0]
    #p = df.loc[df['id_number'] == id_num, 'p_value'].values[0]
    mu = math.log(mu_g) # arithmetic mean is log of geometric mean for lognormal distribution
    sigma = math.log(sigma_g) # standard deviation relationship with geometric standard deviation
    # putting the lognormal parameters in to plot the lognormal distribution
    x_lognorm, y_lognorm = x_nonempty, area*(1/(x_nonempty*sigma*math.sqrt(2*math.pi)))*np.exp((-np.power(np.log(x_nonempty)-mu, 2))/(2*np.power(sigma, 2)))
    # plotting the lognormal fit line
    plt.plot(x_lognorm, y_lognorm, 'r-')
    plt.yscale('log') # log scale for y-axis
    plt.xlim(left=0, right=16) # limits on x-axis
    plt.xlabel('Bin Dry Radius (\u03BCm)') # label on x-axis
    plt.grid() # gridded plot
    plt.title('Sample ' + id_num) # title shows which sample it is
    # creating annotations for geometric mean, geometric standard deviation, chi-squared value,
    # # p-value, sample surface wind, sample buoy wave height, and sample altitude
    plt.annotate('$\u03BC_g$ = %.3f \u03BCm'%(mu_g), xy=(8,630957), size=24, verticalalignment='center')
    plt.annotate('$\u03C3_g$ = %.3f'%(sigma_g), xy=(8,316228), size=24, verticalalignment='center')
    plt.annotate('Reduced $\u03A7^2$ = %.1f'%(chi2), xy=(8,158489), size=24, verticalalignment='center')
    #plt.annotate('$p$ = %.3f'%(p), xy=(12,15000), size=24)
    #plt.annotate('Surface Wind = %.1f m $\mathrm{s^{-1}}$'%(wind_label), xy=(6, 1500), size=24)
    #plt.annotate('Significant Wave Height = %.1f m'%(wave_label), xy=(6, 3000), size=24)
    #plt.annotate('Altitude = %.1f m'%(altitude_label), xy=(6, 6000), size=24)
    plt.tight_layout()
    #ax.set_rasterized(True)
    plt.savefig(plot_dir + '/histogram/synth/synth_histogram_' + id_num + '.png', format='png')
    #plt.savefig(plot_dir + '/histogram/png/histogram_' + id_num + '.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_total_concentration
# Parameters: df, x_variable, y_variable, color_variable, size_variable, x_label, color_label, 
# # size_label.
# Description: This creates a scatter plot. The x-axis is x_variable, and the y-axis is y_variable.
# # The parameter y_variable must always be a type of total number concentration. The x_variable is
# # whatever we want to correlate the total concentration with. The color_variable is what we want
# # to color each scatter point by. The size_variable determines the size of each scatter point.
# # The labels x_label, color_label, and size_label are for the x-axis, colorbar, and legend.
# =================================================================================================
def plot_total_concentration(df, x_variable, y_variable, color_variable, size_variable, x_label, color_label, size_label):
    plt.rcParams['figure.figsize'] = (12.0, 9.0)
    if x_variable=='rh': # drop the samples that have estimated RH values
        df = drop_samples(df, drop_list=no_RH_list)
    # get the variables that you want to use
    x = df[x_variable]
    y = df[y_variable]
    c = df[color_variable]
    s = df[size_variable]
    if y_variable=='cutoff_total_mass' or y_variable=='real_total_salt':
        plt.ylabel('Mass Concentration (\u03BCg $\mathrm{m^{-3}}$)') # label the y-axis
        n_digits = 1
    else:
        plt.ylabel('Number Concentration ($\mathrm{m^{-3}}$)') # label the y-axis
        n_digits = 3
        #plt.ylim(bottom=0, top=11000) # set y-axis limits
    df.sort_values(by=[color_variable], inplace=True) # so that lighter colors appear on top
    # set minimum and maximum of point size and colorbar
    norm_size = [(100 + (300*((val-min(s))/(max(s)-min(s))))) for val in s]
    norm_color = matplotlib.colors.Normalize(vmin=rounddown(c.min(), 1), vmax=roundup(c.max(), 1))
    plt.ylim(bottom=0, top=roundup(max(y), n=n_digits)) # set y-axis limits
    # create the scatter plot
    plt.scatter(x, y, s=norm_size, c=c, cmap=cmap)
    # r-squared analysis
    z = np.polyfit(x, y, 1) # linear polyfit
    p = np.poly1d(z)
    yfit = p(x) # created fitted y values
    # plot the fitted line
    plt.plot(x, yfit, linewidth=2, color='blue')
    # calculate the r-squared value
    ybar = np.sum(y)/len(y)
    ssres = np.sum((y-yfit)**2)
    sstot = np.sum((y-ybar)**2)
    rsquared = 1 - ssres/sstot
    # annotate the equation of the fitted line, and place the annotation above the plot
    if z[1]<0: # if the coefficient of x is negative, then the annotation is slightly different
        plt.annotate('y=%.1fx%.1f'%(z[0],z[1]), xy=(min(x) - (max(x)-min(x))/10, roundup(max(y), n_digits) + roundup(max(y), n_digits)/5), size=24, annotation_clip=False)
    else:
        plt.annotate('y=%.1fx+%.1f'%(z[0],z[1]), xy=(min(x) - (max(x)-min(x))/10, roundup(max(y), n_digits) + roundup(max(y), n_digits)/5), size=24, annotation_clip=False)
    # annotate the r-squared value and place the annotation above the plot
    plt.annotate('$r^2$=%.2f'%(rsquared), xy=(min(x) - (max(x)-min(x))/10, roundup(max(y), n_digits) + roundup(max(y), 1)/10), size=24, annotation_clip=False)
    plt.xlabel(x_label) # label the x-axis
    plt.grid() # give the plot a grid
    # creating the colorbar for the plot
    cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm_color, cmap=cmap))
    cb.set_label(color_label)
    # size labels: minimum value has size of 100 and max has size of 400
    legendMin=plt.scatter([],[], s=100, marker='o', color='black')
    legendMid = plt.scatter([],[], s=250, marker='o', color='black')
    legendMax=plt.scatter([],[], s=400, marker='o', color='black')
    sMin = round(min(s), 2) # rounding the min, mid, and max
    sMid = round((min(s)+max(s))/2, 2)
    sMax = round(max(s), 2)
    # putting the plot legend above the plot
    legend = plt.legend((legendMin, legendMid, legendMax), (sMin, sMid, sMax), scatterpoints=1, bbox_to_anchor=(1.26,1.05), loc='lower right', ncol=3, fontsize=24, title=size_label)
    legend.get_title().set_fontsize('24') # font size of the legend
    plt.tight_layout() # tight layout for the plot
    if 'phng' in x_variable:
        plt.savefig(plot_dir + '/total_concentration/phng/' + y_variable + '_' + x_variable + '_color_' + color_variable + '_size_' + size_variable + '.pdf', format='pdf')
    else:
        plt.savefig(plot_dir + '/total_concentration/' + y_variable + '_' + x_variable + '_color_' + color_variable + '_size_' + size_variable + '.pdf', format='pdf')
    #plt.savefig(plot_dir + '/total_concentration/eps/' + y_variable + '_' + x_variable + '_color_' + color_variable + '_size_' + size_variable + '.eps', format='eps')
    #plt.savefig(plot_dir + '/total_concentration/png/' + y_variable + '_' + x_variable + '_color_' + color_variable + '_size_' + size_variable + '.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_wind_sensitivity
# Parameters: df, id_num
# Description: This creates a histogram representing the size distribution for a particular sample.
# # The size distribution is a number concentration per bin, with each bin having a bin width of 
# # 0.2 microns (e.g. 4.7-4.9 um). Each bin also has an estimated number concentration calculated
# # under the conditions that wind speed is decreased by 35%. This also creates a histogram
# # showing the ratio of the low wind concentration to the observed concentration.
# =================================================================================================
def plot_wind_sensitivity(df, id_num):
    plt.rcParams['figure.figsize'] = (12.0, 9.0) # figure size
    # pulling the bins, observed concentration, and estiamted low wind concentration
    x = df.loc[df['id_number'] == id_num, 'bin_middle'].values[0]
    y = df.loc[df['id_number'] == id_num, 'bin_real_conc'].values[0]
    z = df.loc[df['id_number'] == id_num, 'lowwind_conc'].values[0]
    # getting the bins from y that correspond to nonempty bins in z for comparison purposes
    y_comp = [item if count>0 else 0 for item,count in zip(y,z)]
    y_comp = np.asarray(y_comp) # converting to np array
    z_comp = np.asarray(z) # converting to np array
    error_ratio = z_comp/y_comp # ratio of estimated low wind concentration to observed conc.
    plt.ylabel('Number Concentration ($\mathrm{m^{-3}}$)') # y-axis label
    plt.ylim(bottom=0.1, top=1000000) # y-axis limits
    # get the values for sample altitude, wind, and wave
    altitude_label = df.loc[df['id_number'] == id_num, 'altitude'].values[0]
    wind_label = df.loc[df['id_number'] == id_num, 'surface_wind'].values[0]
    wave_label = df.loc[df['id_number'] == id_num, 'wave_height'].values[0]
    # plot both the concentration (blue) and low wind concentration (red)
    plt.bar(x=x, height=z, width=0.1, alpha=1, color='red')
    plt.bar(x=x, height=y, width=0.1, alpha=1, color='blue')
    #plt.bar(x=x, height=w, width=0.1, alpha=1, color='black')
    plt.yscale('log') # y-axis log scale
    plt.xlim(left=0, right=16) # limits x-axis
    plt.xlabel('Bin Dry Radius (\u03BCm)') # label x-axis
    plt.grid() # gridded plot
    plt.title('Sample ' + id_num) # plot title tells you which sample you are looking at
    # annotation of surface wind, wave height, and altitude
    plt.annotate('Altitude = %.1f m'%(altitude_label), xy=(7, 31622.8), size=24, verticalalignment='center')
    plt.annotate('Significant Wave Height = %.1f m'%(wave_label), xy=(7, 15848.9), size=24, verticalalignment='center')
    plt.annotate('Surface Wind = %.1f m $\mathrm{s^{-1}}$'%(wind_label), xy=(7, 6309.57), size=24, verticalalignment='center')
    # legend for plot
    legendBlue=plt.scatter([],[], s=100, marker='s', color='blue')
    legendRed = plt.scatter([],[], s=100, marker='s', color='red')
    legend = plt.legend((legendBlue, legendRed), ('Unchanged Wind', 'Decreased Wind'), scatterpoints=1, loc='upper right', ncol=1, fontsize=24)
    # plot layout and saving
    plt.tight_layout()
    plt.savefig(plot_dir + '/wind_sensitivity/sensitivity_histogram_' + id_num + '.pdf', format='pdf')
    #plt.savefig(plot_dir + '/wind_sensitivity/eps/sensitivity_histogram_' + id_num + '.eps', format='eps')
    #plt.savefig(plot_dir + '/wind_sensitivity/png/sensitivity_histogram_' + id_num + '.png', format='png')
    plt.close('all')
    # next plot shows the ratio between low wind concentration to observed concentration
    plt.ylabel('Ratio of Calculated Concentration to Observed')
    plt.bar(x=x, height=error_ratio, width=0.1, alpha=1)
    plt.ylim(bottom=0, top=5)
    plt.xlim(left=0, right=16)
    plt.xlabel('Bin Dry Radius (\u03BCm)')
    plt.grid()
    plt.title('Sample ' + id_num)
    # annotation of surface wind, wave height, and altitude
    plt.annotate('Surface Wind = %.1f m $\mathrm{s^{-1}}$'%(wind_label), xy=(7, 4.8), size=24, verticalalignment='center')
    plt.annotate('Significant Wave Height = %.1f m'%(wave_label), xy=(7, 4.5), size=24, verticalalignment='center')
    plt.annotate('Altitude = %.1f m'%(altitude_label), xy=(7, 4.2), size=24, verticalalignment='center')
    # plot layout and saving
    plt.tight_layout()
    plt.savefig(plot_dir + '/wind_sensitivity/ratio/ratio_histogram_' + id_num + '.pdf', format='pdf')
    #plt.savefig(plot_dir + '/wind_sensitivity/eps/ratio_histogram_' + id_num + '.eps', format='eps')
    #plt.savefig(plot_dir + '/wind_sensitivity/png/ratio_histogram_' + id_num + '.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_wind_vs_waves
# Parameters: df, plot_resolution, max_radius, max_wind_speed
# Description: This plots scatter points of each sample with wind direction on the x-axis and
# # wave direction on the y-axis. The points are colored by the buoy wave height and sized by the
# # total concentration observed for each sample.
# =================================================================================================
def plot_wind_vs_waves(df):
    plt.rcParams['figure.figsize'] = (16.0, 9.0)
    x = df['phng_wind_dir'] # wind direction
    y = df['peak_dir'] # wave direction
    c = df['wave_height'] # wave height
    s = df['cutoff_total_conc'] # total concentration
    # setting the size of each point: minimum is 50, maximum is 350
    norm_size = [(50 + (300*((val-min(s))/(max(s)-min(s))))) for val in s]
    # setting the min and max for the colorbar
    norm = matplotlib.colors.Normalize(vmin=c.min(), vmax=c.max())
    xline = np.arange(-30,360,1)
    plt.plot(xline, xline, '-r') # plots straight line where wind and wave direction are same
    plt.scatter(x=x, y=y, s=norm_size, c=c) # plots each sample's wind and wave direction
    # plot labels and limits
    plt.xlim(left=-30,right=180)
    plt.ylim(bottom=-30,top=180)
    plt.xlabel('PHNG Wind Direction (deg)')
    plt.ylabel('Buoy Peak Wave Direction (deg)')
    # colorbar
    cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm))
    cb.set_label('Significant Wave Height (m)')
    # legend
    legendMin=plt.scatter([],[], s=50, marker='o', color='black')
    legendMid = plt.scatter([],[], s=200, marker='o', color='black')
    legendMax=plt.scatter([],[], s=350, marker='o', color='black')
    sMin = round(min(s), 2)
    sMid = round((min(s)+max(s))/2, 2)
    sMax = round(max(s), 2)
    legend = plt.legend((legendMin, legendMid, legendMax), (sMin, sMid, sMax), scatterpoints=1, bbox_to_anchor=(1.26,1.05), loc='upper left', ncol=1, fontsize=24, title='Concentration ($\mathrm{m^{-3}}$)')
    legend.get_title().set_fontsize('24') # legend font size
    # grid and tight layout
    plt.grid()
    plt.tight_layout()
    # title and saving
    #plt.title('Difference Between Wind and Wave Direction')
    plt.savefig(plot_dir + '/wind_wave/wind_wave_direction.pdf', format='pdf')
    #plt.savefig(plot_dir + '/wind_wave/eps/wind_wave_direction.eps', format='eps')
    #plt.savefig(plot_dir + '/wind_wave/png/wind_wave_direction.png', format='png')
    plt.close('all')

# =================================================================================================
# =================================================================================================
# =================================================================================================
# Function Title: plot_wave_orientation, plot_wind_orientation
# Parameters: df, number_bins
# Description: This creates rose plots showing the wind and wave direction for each sample. This
# # basically shows the range of wind and wave direction conditions that we have sampled in.
# =================================================================================================
def plot_wave_orientation(df, number_bins):
    # creates bins based on the number of bins you want
    bins = np.linspace(0.0, 2*np.pi, number_bins, endpoint=False)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='polar') # making it a rose plot
    ax.set_theta_direction(-1) # making the rose plot rotate in a different direction
    ax.set_theta_zero_location("N") # setting 0 to mean North
    ax.set_rticks([5,10,15]) # ticks for the rose plot
    ax.set_rlabel_position(-45) # putting the ticks where there is no data
    y = df.peak_dir*(np.pi/180) # converting the direction to radians
    plt.hist(y, bins) # plotting
    plt.title("All Samples Wave Direction Frequency")
    plt.savefig(plot_dir + '/wind_wave/wave_direction_rose.pdf', format='pdf')
    #plt.savefig(plot_dir + '/wind_wave/eps/wave_direction_rose.eps', format='eps')
    #plt.savefig(plot_dir + '/wind_wave/png/wave_direction_rose.png', format='png')

def plot_wind_orientation(df, number_bins):
    # same thing as plot_wave_direction but now for wind direction
    bins = np.linspace(0.0, 2*np.pi, number_bins, endpoint=False)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='polar')
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("N")
    ax.set_rticks([10,20,30,40])
    ax.set_rlabel_position(-45)
    y = df.phng_wind_dir*(np.pi/180)
    plt.hist(y, bins)
    plt.title("All Samples PHNG Wind Direction Frequency")
    plt.savefig(plot_dir + '/wind_wave/wind_direction_rose.pdf', format='pdf')
    #plt.savefig(plot_dir + '/wind_wave/eps/wind_direction_rose.eps', format='eps')
    #plt.savefig(plot_dir + '/wind_wave/png/wind_direction_rose.png', format='png')


