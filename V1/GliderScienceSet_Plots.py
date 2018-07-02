#!/usr/bin/env python

"""
 Background:
 --------
 GliderScienceSet_Plots.py
 
 
 Purpose:
 --------
 
 History:
 --------


"""
import argparse
import os
from io_utils import ConfigParserLocal
import numpy as np
import xarray as xa

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt


def plot_ts(salt, temp, press, srange=[31,33], trange=[-2,10], ptitle="",labels=True, label_color='k', bydepth=False): 
    plt.style.use('ggplot')
    
    # Figure out boudaries (mins and maxs)
    smin = srange[0]
    smax = srange[1]
    tmin = trange[0]
    tmax = trange[1]

    # Calculate how many gridcells we need in the x and y dimensions
    xdim = int(round((smax-smin)/0.1+1,0))
    ydim = int(round((tmax-tmin)+1,0))
    
    #print 'ydim: ' + str(ydim) + ' xdim: ' + str(xdim) + ' \n'
    if (xdim > 10000) or (ydim > 10000): 
        print('To many dimensions for grid in file. Likely  missing data \n')
        return
 
    # Create empty grid of zeros
    dens = np.zeros((ydim,xdim))
 
    # Create temp and salt vectors of appropiate dimensions
    ti = np.linspace(0,ydim-1,ydim)+tmin
    si = np.linspace(0,xdim-1,xdim)*0.1+smin
 
    # Loop to fill in grid with densities
    for j in range(0,int(ydim)):
        for i in range(0, int(xdim)):
            dens[j,i]=sw.dens0(si[i],ti[j])
 
    # Substract 1000 to convert to sigma-t
    dens = dens - 1000
 
    # Plot data ***********************************************
    
    ax1 = fig.add_subplot(111)
    if labels:
        CS = plt.contour(si,ti,dens, linestyles='dashed', colors='k')

        
    if labels:
        plt.clabel(CS, fontsize=12, inline=1, fmt='%1.1f') # Label every second level
        
    if bydepth:
        ts = ax1.scatter(salt,temp, c=press, cmap='gray', s=10)
    else:
        ts = ax1.scatter(salt,temp,s=10,c=label_color)
        
    plt.ylim(tmin,tmax)
    plt.xlim(smin,smax)
    if labels:
        if bydepth:
            plt.colorbar(ts )
 
        ax1.set_xlabel('Salinity (PSU)')
        ax1.set_ylabel('Temperature (C)')

    
        t = fig.suptitle(ptitle, fontsize=12, fontweight='bold')
        t.set_y(1.08)
    return fig  

"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Plot archived NetCDF glider data and Science Data')
parser.add_argument('ofilepath', metavar='ofilepath', type=str,
    help='path to directory with UW initial Oculus  netcdf data')
parser.add_argument('sfilepath', metavar='sfilepath', type=str,
    help='path to directory with Oculus Science Data netcdf data')
parser.add_argument('profileid',metavar='profileid', type=str,
    help='divenumber - eg p4010260')
args = parser.parse_args()


isUW, ismerged, isup, isdown = True, True, True, True
# There are potentially three files - original UW file, a merged file and an upcast/downcast file
filein = args.ofilepath + args.profileid + '.nc'
try:
  df = xa.open_dataset(filein, autoclose=True)
except IOError:
  isUW = False
  
filein_m = args.sfilepath + args.profileid + '_m.nc'
ismerged = True
try:
  df_m = xa.open_dataset(filein_m, autoclose=True)
except IOError:
  ismerged = False

filein_u = args.sfilepath + args.profileid + '_u.nc'
try:
  df_u = xa.open_dataset(filein_u, autoclose=True)
except IOError:
  isup = False

filein_d = args.sfilepath + args.profileid + '_d.nc'
try:
  df_d = xa.open_dataset(filein_d, autoclose=True)
except IOError:
  isdown = False



fig = plt.figure(figsize=(6, 6))
if isUW:
  fig = plot_ts(df.salinity,df.temperature,df.depth,labels=True,label_color='g')
  print("Added original data")
if ismerged:
  fig = plot_ts(df_m.Salinity,df_m.Temperature,df_m.Pressure,labels=False,label_color='k')
  print("Added merged data")
if isup:
  fig = plot_ts(df_u.Salinity,df_u.Temperature,df_u.Pressure,labels=False,label_color='b')
  print("Added binned upcast data")
if isdown:
  fig = plot_ts(df_d.Salinity,df_d.Temperature,df_d.Pressure,labels=False,label_color='r')
  print("Added binned downcast data")

