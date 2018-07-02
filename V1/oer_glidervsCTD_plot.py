#!/usr/bin/env python

"""
 Background:
 --------
 oer_glidervsCTD_plot.py
 
 
 Purpose:
 --------
 
 History:
 --------


"""
import argparse, os

import numpy as np

import calc.aanderaa_corrO2_sal as optode_O2_corr
from plots.profile_plot import CTDProfilePlot
import io_utils.EcoFOCI_netCDF_read as eFOCI_ncread

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt


def castdirection(depth):
    """determin index of upcast and downcast"""
    downcast = [0,np.argmax(np.diff(depth)<0)+1]
    upcast = [np.argmax(np.diff(depth)<0),len(depth)]

    return (downcast,upcast)

"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Plot archived NetCDF glider data against NetCDF CTD cast')
parser.add_argument('glider_file', metavar='glider_file', type=str,
               help='complete path to netcdf glider file')
parser.add_argument('ctd_file', metavar='glider_file', type=str,
               help='complete path to netcdf ctd file')

args = parser.parse_args()



#######################
#
# Data Ingest and Processing


filein = args.glider_file
diveNum = filein.split('/')[-1].split('.nc')[0]

df = eFOCI_ncread.EcoFOCI_netCDF(file_name=filein)
vars_dic = df.get_vars()
ncdata = df.ncreadfile_dic()
data_time = df.epochtime2date()
df.close()

### Dive Data
pressure = ncdata['ctd_pressure']
SBE_Temperature = ncdata['temperature']
SBE_Salinity = ncdata['salinity']

Wetlabs_CDOM = ncdata['wlbb2fl_sig470nm_adjusted']
Wetlabs_CHL  = ncdata['wlbb2fl_sig695nm_adjusted']
Wetlabs_NTU  = ncdata['wlbb2fl_sig700nm_adjusted']

Aand_Temp = ncdata['eng_aa4330_Temp']
#Aand_O2_corr = ncdata['aanderaa4330_dissolved_oxygen']
#Aand_O2_corr = ncdata['eng_aa4330_O2']
Aand_O2_corr = optode_O2_corr.O2_dep_comp(oxygen_conc=ncdata['eng_aa4330_O2'],
                                     depth=ncdata['depth']/100)
Aand_O2_corr = optode_O2_corr.O2_sal_comp(oxygen_conc=Aand_O2_corr,
                                     salinity=SBE_Salinity,
                                     temperature=SBE_Temperature)
Aand_DO = optode_O2_corr.O2_molar2umkg(oxygen_conc=Aand_O2_corr,
                                     salinity=SBE_Salinity,
                                     temperature=SBE_Temperature,
                                     pressure=pressure) 
Aand_O2_corr = Aand_DO
Aand_DO_Sat  = ncdata['eng_aa4330_AirSat']
Aand_DO_Sat_calc = optode_O2_corr.O2PercentSat(oxygen_conc=Aand_O2_corr, 
                                     salinity=SBE_Salinity,
                                     temperature=SBE_Temperature,
                                     pressure=pressure)  

PAR_satu = ncdata['eng_satu_PARuV'] * 1000
PAR_satd = ncdata['eng_satd_PARuV'] * 1000

lat = ncdata['log_gps_lat'][0]
lon = ncdata['log_gps_lon'][0]

"""---------"""
filein = args.ctd_file

df = eFOCI_ncread.EcoFOCI_netCDF(file_name=filein)
vars_dic = df.get_vars()
ncdata = df.ncreadfile_dic()
#ctd_data_time = df.epochtime2date()
df.close()

### CTD Data
CTD_pressure = ncdata['P_1'][0,:,0,0]
CTD_Temperature = ncdata['T_28'][0,:,0,0]
CTD_Salinity = ncdata['S_41'][0,:,0,0]

CTD_Wetlabs_CHL  = ncdata['F_903'][0,:,0,0]

CTD_O2_corr = ncdata['O_65'][0,:,0,0]
CTD_DO_Sat  = ncdata['OST_62'][0,:,0,0]


#######################
#
# Plots

GliderPlot = CTDProfilePlot()
downInd,upInd = castdirection(pressure)

if not os.path.exists('images/dive' + diveNum ):
    os.makedirs('images/dive' + diveNum)

########## CTD
### temperature
(plt, fig) = GliderPlot.plot1plot_CTD(epic_key=['T_28','T_28u','T2_35','T2_35u','temperature'],
                 xdata=[SBE_Temperature[downInd[0]:downInd[1]],SBE_Temperature[upInd[0]:upInd[1]],
                        Aand_Temp[downInd[0]:downInd[1]],Aand_Temp[upInd[0]:upInd[1]],CTD_Temperature],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]],CTD_pressure],
                 xlabel='Temperature (C)',
                 updown=['d','u','d','u',''],
                 maxdepth=np.max(pressure))

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=data_time[0],
                  lat=lat,
                  lon=lon)

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_temperature.png', bbox_inches='tight', dpi = (300))
plt.close()

###salinity
(plt, fig) = GliderPlot.plot1plot_CTD(epic_key=['S_41','S_41u','salinity'],
                 xdata=[SBE_Salinity[downInd[0]:downInd[1]],SBE_Salinity[upInd[0]:upInd[1]],CTD_Salinity],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]],CTD_pressure],
                 xlabel='Salinity (PSU)',
                 updown=['d','u',''],
                 maxdepth=np.max(pressure))

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=data_time[0],
                  lat=lat,
                  lon=lon)

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_salinity.png', bbox_inches='tight', dpi = (300))
plt.close()

##### optode
### conc
(plt, fig) = GliderPlot.plot1plot_CTD(epic_key=['O_65','O_65u','oxy_conc'],
                 xdata=[Aand_O2_corr[downInd[0]:downInd[1]],Aand_O2_corr[upInd[0]:upInd[1]],CTD_O2_corr],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]],CTD_pressure],
                 xlabel='Oxygen Conc (umole/kg)',
                 updown=['d','u',''],
                 maxdepth=np.max(pressure))

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=data_time[0],
                  lat=lat,
                  lon=lon)

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_O2Conc.png', bbox_inches='tight', dpi = (300))
plt.close()

### PSat
(plt, fig) = GliderPlot.plot1plot_CTD(epic_key=['OST_62','OST_62u','oxy_sat'],
                 xdata=[Aand_DO_Sat[downInd[0]:downInd[1]],Aand_DO_Sat[upInd[0]:upInd[1]],CTD_DO_Sat],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]],CTD_pressure],
                 xlabel='Oxygen PSat (%)',
                 updown=['d','u',''],
                 maxdepth=np.max(pressure))

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=data_time[0],
                  lat=lat,
                  lon=lon)

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_O2Psat.png', bbox_inches='tight', dpi = (300))
plt.close()

########## WetLabs
###chl
(plt, fig) = GliderPlot.plot1plot_CTD(epic_key=['Chl_933','Chl_933u','chlor'],
                 xdata=[Wetlabs_CHL[downInd[0]:downInd[1]],Wetlabs_CHL[upInd[0]:upInd[1]],CTD_Wetlabs_CHL],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]],CTD_pressure],
                 xlabel='Chl (ug/l)',
                 updown=['d','u',''],
                 maxdepth=np.max(pressure))

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=data_time[0],
                  lat=lat,
                  lon=lon)

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_chl.png', bbox_inches='tight', dpi = (300))
plt.close()

