# =================================================================================================
# =================================================================================================
# =================================================================================================
# Title: Ranz Wong
# Author: Chung Taing
# Date Updated: 10 April 2020
# Description: This script calculates collision efficiency for particles in an air stream
# impacting a ribbon of infinite length and finite width.
# =================================================================================================
# =================================================================================================
# =================================================================================================

# import packages
import math

# from Pruppacher, H.R. and Klett, J.D. (1997) Microphysics of Clouds and Precipitation 2nd edition
# see equations 10-139 and 10-140
# define standard pressure (Pa), temperature (K), and mean free path (m)
std_pressure = 101325
std_temperature = 273.16
std_mean_free_path = 6.6e-8 # standard mean free path at room temperature and at 1013 mb in meters

# define other constants
slide_width = 6.35e-3 # width of the ribbon of infinite length (our slides) in meters
salt_density = 2.163e3 # density of NaCl particles in kg per meter cubed

# dynamic viscosity of air dependent on temperature
# "[...] the dynamic viscosity for other than standard conditions is given with an accuracy of +- 0.002e-4 poise by"
# from Pruppacher, H.R. and Klett, J.D. (1997) Microphysics of Clouds and Precipitation 2nd edition
# equations 10-141a and 10-141b
# n (poise) = (1.718 + 0.0049T) * 10^-4 (T is in Celsius and T >= 0 C)
# n (poise) = (1.718 + 0.0049T - (1.2e-5)*T^2) * 10^-4 (T is in Celsius and T < 0 C)
# 1 Pascal*second = 10 poise, thus to convert to SI units need to divide everything by 10
def get_dyn_visc(t_kelvin):
    if t_kelvin >= 273.16 :
        dyn_visc = 1.718e-5 + (4.9e-8)*(t_kelvin-273.16)
    else:
        dyn_visc = 1.718e-5 + (4.9e-8)*(t_kelvin-273.16) - (1.2e-10)*(t_kelvin-273.16)**2
    return dyn_visc

# dry radius vs radius at equilibrium RH
# RH in fractional form
# from Lewis, E.R. (2008) An examination of Kohler theory [...]
# r/rdry = a*[b + 1 / (1 - rh + (e0/a)^(3/2))]^(1/3)
# e0 = r0/rdry where r0 = characteristic length scale for Kelvin effect
# for pure water (infinite dilution), r0 = 1.1 nm = 1.1e-9 m
# for NaCl, a = 1.08 and b = 1.10
# dryRadius in meters, relHum as a fraction
def get_wet_radius(dry_radius, rh):
    e_pure = 1.1e-9/dry_radius
    wet_radius = dry_radius*1.08*(1.1 + 1/(1 - rh + (e_pure/1.08)**(3/2)))**(1/3)
    return wet_radius

# Cunningham (1910) correction factor for resistance of a gas to movement of small particles (drag)
# "The Cunningham correction factor becomes significant when particles become smaller than 15 micrometers, for air at ambient conditions."
# cFactor = 1 + alpha*meanFreePath/ssaRadius
# alpha = A1 + A2*exp(-A3*2*ssaRadius/meanFreePath)
# for air (Davis, 1945): A1=1.257, A2=0.4, A3=0.55
# ssaRadius is radius of particle in meters
# mean free path (in m) depending on pressure (in Pa) and temperature (in K)
# from Pruppacher, H.R. and Klett, J.D. (1997) Microphysics of Clouds and Precipitation 2nd edition
# equation 10-140
def get_cunningham_factor(ssa_radius, pressure, temperature):
    mean_free_path = std_mean_free_path*(std_pressure/pressure)*(temperature/std_temperature)
    alpha = 1.257 + 0.4*math.exp(-1.1*ssa_radius/mean_free_path)
    c_factor = 1 + alpha*mean_free_path/ssa_radius
    return c_factor

# returns ranz-wong collision efficiency for aerosol stream impaction on an infinite ribbon
# pressure in pascals, temperature in Kelvin, airSpeed in meter per second, relHum in fraction, radius in meters
def get_collision_efficiency(pressure, temperature, air_speed, rh, dry_radius):
    ssa_radius = get_wet_radius(dry_radius, rh)
    salt_volume = (4/3)*math.pi*dry_radius**3
    salt_mass = salt_volume*salt_density
    ssa_volume = (4/3)*math.pi*ssa_radius**3
    water_volume = ssa_volume - salt_volume
    water_mass = water_volume*1000 # 1000 is the density of water in kg permeter cubed
    ssa_density = (salt_mass + water_mass)/ssa_volume
    c_factor = get_cunningham_factor(ssa_radius, pressure, temperature)
    dyn_visc = get_dyn_visc(temperature)
    air_density = pressure/(287.04*temperature) # 287.04 is specific gas constant for dry air
    # psi is the "ratio of the force necessary to stop a particle traveling at velocity in the distance slideWidth/2"
    psi = (c_factor*ssa_density*air_speed*((2*ssa_radius)**2))/(18*dyn_visc*slide_width)
    if psi < 0.125 :
        collision_efficiency = 0
    else:
        q = math.sqrt(0.5/psi - 1/(16*psi**2))
        t = (1/q)*math.atan(4*psi*q/(4*psi - 1))
        s1 = -0.25/psi + math.sqrt(1/(16*psi**2) + 0.5/psi)
        s2 = -0.25/psi - math.sqrt(1/(16*psi**2) + 0.5/psi)
        collision_efficiency = (s2 - s1)/(s2*math.exp(s1*t) - s1*math.exp(s2*t))
    return collision_efficiency
