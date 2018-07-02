#!/usr/bin/env python

"""
 Background:
 --------
 oer_glider_plot.py
 
 
 Purpose:
 --------
 
 History:
 --------


"""
import argparse

from io_utils import ConfigParserLocal

import calc.aanderaa_corrO2_sal as optode_O2_corr
from plots.profile_plot import CTDProfilePlot
import io_utils.glider_functions as glider

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt


"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Plot raw Glider Data')
parser.add_argument('sourcefile', metavar='sourcefile', type=str,
               help='complete path to epic file')
parser.add_argument('cal_file', metavar='cal_file', type=str,
               help='complete path to yaml instrument calibration file')
parser.add_argument('divenum', metavar='divenum', type=str,
               help='dive number')
args = parser.parse_args()



#######################
#
# Data Ingest and Processing


filein = args.sourcefile
diveNum = args.divenum

rawdata, data_obj = glider.get_inst_data(filein, MooringID='oculus_test')

data_time = data_obj.elapsedtime2date()

pressure = data_obj.depth2press()

cal_file = ConfigParserLocal.get_config(args.cal_file,ftype='yaml')

SBE_Temperature = data_obj.sbe_temp(cal_file['SBE_Temp_Coeffs'])


SBE_Conductivity = data_obj.sbe_cond(cal_file['SBE_Cond_Coeffs'])

SBE_Salinity = glider.cond2salinity(SBE_Conductivity,SBE_Temperature,pressure)
SBE_Salinity[np.where(SBE_Salinity<20)] = np.nan

Wetlabs_CDOM = data_obj.wetlabs_cdom(cal_file['Wetlabs_470nm_Coeffs'],varname='wlbb2fl.sig470nm')
Wetlabs_CHL  = data_obj.wetlabs_chl(cal_file['Wetlabs_CHL_Coeffs'],varname='wlbb2fl.sig695nm')
Wetlabs_NTU  = data_obj.wetlabs_ntu(cal_file['Wetlabs_700nm_Coeffs'],varname='wlbb2fl.sig700nm')

# apply salinity and depth corrections to oxygen optode and recalc percentsat
Aand_O2_corr = optode_O2_corr.O2_dep_comp(oxygen_conc=rawdata['aa4330.O2'],
                                     depth=rawdata['depth']/100)
Aand_O2_corr = optode_O2_corr.O2_sal_comp(oxygen_conc=Aand_O2_corr,
                                     salinity=SBE_Salinity,
                                     temperature=SBE_Temperature)
Aand_DO = optode_O2_corr.O2_molar2umkg(oxygen_conc=Aand_O2_corr,
                                     salinity=SBE_Salinity,
                                     temperature=SBE_Temperature,
                                     pressure=pressure)              
Aand_DO_Sat = optode_O2_corr.O2PercentSat(oxygen_conc=Aand_O2_corr, 
                                     salinity=SBE_Salinity,
                                     temperature=SBE_Temperature,
                                     pressure=pressure)  



#######################
#
# Plots

GliderPlot = CTDProfilePlot()
downInd,upInd = data_obj.castdirection()

########## CTD
### temperature
(plt, fig) = GliderPlot.plot1plot(epic_key=['T_28','T_28u','T2_35','T2_35u'],
                 xdata=[SBE_Temperature[downInd[0]:downInd[1]],SBE_Temperature[upInd[0]:upInd[1]],
                        rawdata['aa4330.Temp'][downInd[0]:downInd[1]],rawdata['aa4330.Temp'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Temperature (C)',
                 updown=['d','u','d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'_temperature.png', bbox_inches='tight', dpi = (300))
plt.close()

###salinity
(plt, fig) = GliderPlot.plot1plot(epic_key=['S_41','S_41u'],
                 xdata=[SBE_Salinity[downInd[0]:downInd[1]],SBE_Salinity[upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Salinity (PSU)',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'_salinity.png', bbox_inches='tight', dpi = (300))
plt.close()

##### optode
### conc
(plt, fig) = GliderPlot.plot1plot(epic_key=['OST_62','OST_62u','CTDOST_4220','CTDOST_4220u'],
                 xdata=[Aand_DO[downInd[0]:downInd[1]],Aand_DO[upInd[0]:upInd[1]],
                        rawdata['aa4330.O2'][downInd[0]:downInd[1]],rawdata['aa4330.O2'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Oxygen Conc (ug/m^3 // ug/l)',
                 updown=['d','u','d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'_O2Conc.png', bbox_inches='tight', dpi = (300))
plt.close()

### PSat
(plt, fig) = GliderPlot.plot1plot(epic_key=['O_65','O_65u','CTDOXY_4221','CTDOXY_4221u'],
                 xdata=[Aand_DO_Sat[downInd[0]:downInd[1]],Aand_DO_Sat[upInd[0]:upInd[1]],
                        rawdata['aa4330.AirSat'][downInd[0]:downInd[1]],rawdata['aa4330.AirSat'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Oxygen PSat (%)',
                 updown=['d','u','d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'_O2Psat.png', bbox_inches='tight', dpi = (300))
plt.close()

########## PAR
### Up/Down Welling
(plt, fig) = GliderPlot.plot1plot(epic_key=['PAR_905','PAR_905u','PAR_917','PAR_917u'],
                 xdata=[rawdata['satu.PARuV'][downInd[0]:downInd[1]],rawdata['satu.PARuV'][upInd[0]:upInd[1]],
                        rawdata['satd.PARuV'][downInd[0]:downInd[1]],rawdata['satd.PARuV'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='PAR (uE m-2 s) (darker is upward looking, lighter is downard looking) ',
                 updown=['d','u','d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'_PAR.png', bbox_inches='tight', dpi = (300))
plt.close()

########## WetLabs
###chl
(plt, fig) = GliderPlot.plot1plot(epic_key=['Chl_933','Chl_933u'],
                 xdata=[Wetlabs_CHL[downInd[0]:downInd[1]],Wetlabs_CHL[upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Chl (ug/l)',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'_chl.png', bbox_inches='tight', dpi = (300))
plt.close()

###cdom
(plt, fig) = GliderPlot.plot1plot(epic_key=['CDOM_2980','CDOM_2980u'],
                 xdata=[Wetlabs_CDOM[downInd[0]:downInd[1]],Wetlabs_CDOM[upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='CDOM (ppb)',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'_cdom.png', bbox_inches='tight', dpi = (300))
plt.close()

###turb
(plt, fig) = GliderPlot.plot1plot(epic_key=['Trb_980','Trb_980u'],
                 xdata=[Wetlabs_NTU[downInd[0]:downInd[1]],Wetlabs_NTU[upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Turbidity (NTU)',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

plt.savefig('images/dive'+diveNum+'_turbidity.png', bbox_inches='tight', dpi = (300))
plt.close()


## plot postion parameters as function of time
(plt, fig) = GliderPlot.plot1plot(epic_key=['P_1','P_1u'],
                 xdata=[rawdata['elaps_t'][downInd[0]:downInd[1]],rawdata['elaps_t'][upInd[0]:upInd[1]]],
                 ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                 xlabel='Elapsed Time',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

plt.savefig('images/dive'+diveNum+'_depthvtime.png', bbox_inches='tight', dpi = (300))
plt.close()

###
(plt, fig) = GliderPlot.plot1plot(epic_key=['pitch','pitch_u'],
                 xdata=[rawdata['elaps_t'][downInd[0]:downInd[1]],rawdata['elaps_t'][upInd[0]:upInd[1]]],
                 ydata=[rawdata['pitchAng'][downInd[0]:downInd[1]],rawdata['pitchAng'][upInd[0]:upInd[1]]],
                 xlabel='Elapsed Time',
                 ylabel='',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

plt.savefig('images/dive'+diveNum+'_pitchvtime.png', bbox_inches='tight', dpi = (300))
plt.close()

###
(plt, fig) = GliderPlot.plot1plot(epic_key=['roll','roll_u'],
                 xdata=[rawdata['elaps_t'][downInd[0]:downInd[1]],rawdata['elaps_t'][upInd[0]:upInd[1]]],
                 ydata=[rawdata['rollAng'][downInd[0]:downInd[1]],rawdata['rollAng'][upInd[0]:upInd[1]]],
                 xlabel='Elapsed Time',
                 ylabel='',
                 updown=['d','u'])

ptitle = GliderPlot.add_title(cruiseid='',
                  fileid=filein.split('/')[-1],
                  castid=diveNum,
                  castdate=header_data['time_start'])

t = fig.suptitle(ptitle)
t.set_y(1.06)
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

plt.savefig('images/dive'+diveNum+'_rollvtime.png', bbox_inches='tight', dpi = (300))
plt.close()