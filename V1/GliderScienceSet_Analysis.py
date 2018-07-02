#!/usr/bin/env python

"""
 Background:
 --------
 GliderScienceSet_Analysis.py
 
 
 Purpose:
 --------
 
 History:
 --------


"""

# System Stack
import argparse
import os
from io_utils import ConfigParserLocal

# Science Stack
import numpy as np
import xarray as xa
import seawater as sw

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt


def find_max_inversion(temperature=None,salinity=None,pressure=None):
    sigmat = sw.dens(s=salinity,t=temperature,p=pressure) - 1000.
    dtdz = np.gradient(sigmat,pressure)

    return np.nanmin(dtdz),np.nanargmin(dtdz)


"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Analyze archived NetCDF glider data and Science Data')
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



if isUW:
  val,ind = find_max_inversion(salinity=df.salinity,
                               temperature=df.temperature,
                               pressure=df.depth)
  print("{} Max Delta SigmaT original data {}".format(args.profileid,val))
if ismerged:
  val,ind = find_max_inversion(salinity=df_m.Salinity,
                               temperature=df_m.Temperature,
                               pressure=df_m.Pressure)
  print("{} Max Delta SigmaT merged data {}".format(args.profileid+'_m',val))
if isup:
  val,ind = find_max_inversion(salinity=df_u.Salinity,
                               temperature=df_u.Temperature,
                               pressure=df_u.Pressure)
  print("{} Max Delta SigmaT binned upcast data {}".format(args.profileid+'_u',val))
if isdown:
  val,ind = find_max_inversion(salinity=df_d.Salinity,
                               temperature=df_d.Temperature,
                               pressure=df_d.Pressure)
  print("{} Max Delta SigmaT binned downcast data {}".format(args.profileid+'_d',val))

