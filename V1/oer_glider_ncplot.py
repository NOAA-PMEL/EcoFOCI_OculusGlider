#!/usr/bin/env python

"""
 Background:
 --------
 oer_glider_ncplot.py
 
 
 Purpose:
 --------
 
 History:
 --------


"""
import argparse, os

from io_utils import ConfigParserLocal
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

parser = argparse.ArgumentParser(description='Plot archived NetCDF glider data')
parser.add_argument('-ini','--ini_file', type=str,
               help='complete path to yaml instrument ini (state) file')
parser.add_argument('-cf','--cal_file', type=str,
               help='complete path to yaml instrument calibration file')
args = parser.parse_args()



#######################
#
# Data Ingest and Processing
state_config = ConfigParserLocal.get_config(args.ini_file,ftype='yaml')
ncfile_list = [state_config['base_id'] + str(item).zfill(4) for item in range(state_config['startnum'],state_config['endnum'],1)]

for fid in ncfile_list:
  diveNum = fid
  filein = state_config['path'] + fid + '.nc'

  print("Working on file {file}".format(file=filein))

  try:
    df = eFOCI_ncread.EcoFOCI_netCDF(file_name=filein)
    vars_dic = df.get_vars()
    ncdata = df.ncreadfile_dic()
    data_time = df.epochtime2date()
    df.close()
  except IOError:
    continue
  
  try:  
    pressure = ncdata['ctd_pressure']
    SBE_Temperature = ncdata['temperature']
    SBE_Temperature[SBE_Temperature > 20] = np.nan
    SBE_Salinity = ncdata['salinity']
    SBE_Salinity[SBE_Salinity < 28] = np.nan
    SBE_Salinity_raw = ncdata['salinity_raw']
    SBE_Salinity_raw[SBE_Salinity_raw < 28] = np.nan

    Wetlabs_CDOM = ncdata['wlbb2fl_sig470nm_adjusted']
    Wetlabs_CHL  = ncdata['wlbb2fl_sig695nm_adjusted']
    Wetlabs_NTU  = ncdata['wlbb2fl_sig700nm_adjusted']

    Aand_Temp = ncdata['eng_aa4330_Temp']
    Aand_Temp[Aand_Temp > 20] = np.nan
    Aand_O2_corr = ncdata['aanderaa4330_dissolved_oxygen']
    Aand_O2_corr[Aand_O2_corr >= 1000] = np.nan
    Aand_DO_Sat  = ncdata['eng_aa4330_AirSat']
    Aand_DO_Sat[Aand_DO_Sat <= 0] = np.nan
    Aand_DO_Sat[Aand_DO_Sat > 200] = np.nan
    Aand_DO_Sat_calc = optode_O2_corr.O2PercentSat(oxygen_conc=Aand_O2_corr, 
                                         salinity=SBE_Salinity_raw,
                                         temperature=SBE_Temperature,
                                         pressure=pressure)  

    PAR_satu = ncdata['eng_satu_PARuV'] * 1000
    PAR_satd = ncdata['eng_satd_PARuV'] * 1000

    lat = ncdata['log_gps_lat'][0]
    lon = ncdata['log_gps_lon'][0]
  except KeyError:
    continue

  ### look for engineering values if qc'd science values look off
  if args.cal_file:
      cal_file = ConfigParserLocal.get_config(args.cal_file,ftype='yaml')
      #eng_sbect_tempFreq
      SBE_Temperature = data_obj.sbe_temp(cal_file['SBE_Temp_Coeffs'])
      SBE_Conductivity = data_obj.sbe_cond(cal_file['SBE_Cond_Coeffs'])

      SBE_Salinity_raw = glider.cond2salinity(SBE_Conductivity,SBE_Temperature,pressure)
      SBE_Salinity_raw[np.where(SBE_Salinity_raw<20)] = np.nan

      Wetlabs_CDOM = data_obj.wetlabs_cdom(cal_file['Wetlabs_470nm_Coeffs'],varname='wlbb2fl.sig470nm')
      Wetlabs_CHL  = data_obj.wetlabs_chl(cal_file['Wetlabs_CHL_Coeffs'],varname='wlbb2fl.sig695nm')
      Wetlabs_NTU  = data_obj.wetlabs_ntu(cal_file['Wetlabs_700nm_Coeffs'],varname='wlbb2fl.sig700nm')

      # apply salinity and depth corrections to oxygen optode and recalc percentsat
      Aand_O2_corr = optode_O2_corr.O2_dep_comp(oxygen_conc=rawdata['aa4330.O2'],
                                         depth=rawdata['depth']/100)
      Aand_O2_corr = optode_O2_corr.O2_sal_comp(oxygen_conc=Aand_O2_corr,
                                         salinity=SBE_Salinity_raw,
                                         temperature=SBE_Temperature)
      Aand_DO = optode_O2_corr.O2_molar2umkg(oxygen_conc=Aand_O2_corr,
                                         salinity=SBE_Salinity_raw,
                                         temperature=SBE_Temperature,
                                         pressure=pressure)              
      Aand_DO_Sat = optode_O2_corr.O2PercentSat(oxygen_conc=Aand_O2_corr, 
                                         salinity=SBE_Salinity_raw,
                                         temperature=SBE_Temperature,
                                         pressure=pressure)  

      downInd,upInd = data_obj.castdirection()

  #######################
  #
  # Plots

  GliderPlot = CTDProfilePlot()
  downInd,upInd = castdirection(pressure)

  if not os.path.exists('images/dive' + diveNum ):
      os.makedirs('images/dive' + diveNum)

  ########## CTD
  ### temperature
  (plt, fig) = GliderPlot.plot1plot(epic_key=['T_28','T_28u','T2_35','T2_35u'],
                   xdata=[SBE_Temperature[downInd[0]:downInd[1]],SBE_Temperature[upInd[0]:upInd[1]],
                          Aand_Temp[downInd[0]:downInd[1]],Aand_Temp[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='Temperature (C)',
                   updown=['d','u','d','u'],
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
  (plt, fig) = GliderPlot.plot1plot(epic_key=['S_41','S_41u','S_42','S_42u'],
                   xdata=[SBE_Salinity_raw[downInd[0]:downInd[1]],SBE_Salinity_raw[upInd[0]:upInd[1]],
                        SBE_Salinity[downInd[0]:downInd[1]],SBE_Salinity[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='Salinity (PSU)',
                   updown=['d','u','d','u'],
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
  (plt, fig) = GliderPlot.plot1plot(epic_key=['O_65','O_65u'],
                   xdata=[Aand_O2_corr[downInd[0]:downInd[1]],Aand_O2_corr[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='Oxygen Conc (umole/kg)',
                   updown=['d','u'],
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
  (plt, fig) = GliderPlot.plot1plot(epic_key=['OST_62','OST_62u'],
                   xdata=[Aand_DO_Sat[downInd[0]:downInd[1]],Aand_DO_Sat[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='Oxygen PSat (%)',
                   updown=['d','u'],
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

  ########## PAR
  ### Up/Down Welling
  (plt, fig) = GliderPlot.plot1plot(epic_key=['PAR_905','PAR_905u','PAR_917','PAR_917u'],
                   xdata=[PAR_satu[downInd[0]:downInd[1]],PAR_satu[upInd[0]:upInd[1]],
                          PAR_satd[downInd[0]:downInd[1]],PAR_satd[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='PAR (uE m-2 s) (darker is upward looking, lighter is downard looking) ',
                   updown=['d','u','d','u'],
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

  plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_PAR.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ########## WetLabs
  ###chl
  (plt, fig) = GliderPlot.plot1plot(epic_key=['Chl_933','Chl_933u'],
                   xdata=[Wetlabs_CHL[downInd[0]:downInd[1]],Wetlabs_CHL[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='Chl (ug/l)',
                   updown=['d','u'],
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

  ###cdom
  (plt, fig) = GliderPlot.plot1plot(epic_key=['CDOM_2980','CDOM_2980u'],
                   xdata=[Wetlabs_CDOM[downInd[0]:downInd[1]],Wetlabs_CDOM[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='CDOM (ppb)',
                   updown=['d','u'],
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

  plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_cdom.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ###turb
  (plt, fig) = GliderPlot.plot1plot(epic_key=['Trb_980','Trb_980u'],
                   xdata=[Wetlabs_NTU[downInd[0]:downInd[1]],Wetlabs_NTU[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='Turbidity (NTU)',
                   updown=['d','u'],
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

  plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_turbidity.png', bbox_inches='tight', dpi = (300))
  plt.close()


  ## plot postion parameters as function of time
  (plt, fig) = GliderPlot.plot1plot(epic_key=['P_1','P_1u'],
                   xdata=[data_time[downInd[0]:downInd[1]],data_time[upInd[0]:upInd[1]]],
                   ydata=[pressure[downInd[0]:downInd[1]],pressure[upInd[0]:upInd[1]]],
                   xlabel='Elapsed Time',
                   updown=['d','u'],
                   xisdatetime=True)

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid=filein.split('/')[-1],
                    castid=diveNum,
                    castdate=data_time[0],
                    lat=lat,
                    lon=lon)

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

  plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_depthvtime.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ###
  (plt, fig) = GliderPlot.plot1plot(epic_key=['pitch','pitch_u'],
                   xdata=[data_time[downInd[0]:downInd[1]],data_time[upInd[0]:upInd[1]]],
                   ydata=[ncdata['eng_pitchAng'][downInd[0]:downInd[1]],ncdata['eng_pitchAng'][upInd[0]:upInd[1]]],
                   xlabel='Elapsed Time',
                   ylabel='',
                   updown=['d','u'],
                   xisdatetime=True)

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid=filein.split('/')[-1],
                    castid=diveNum,
                    castdate=data_time[0],
                    lat=lat,
                    lon=lon)

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

  plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_pitchvtime.png', bbox_inches='tight', dpi = (300))
  plt.close()

  ###
  (plt, fig) = GliderPlot.plot1plot(epic_key=['roll','roll_u'],
                   xdata=[data_time[downInd[0]:downInd[1]],data_time[upInd[0]:upInd[1]]],
                   ydata=[ncdata['eng_rollAng'][downInd[0]:downInd[1]],ncdata['eng_rollAng'][upInd[0]:upInd[1]]],
                   xlabel='Elapsed Time',
                   ylabel='',
                   updown=['d','u'],
                   xisdatetime=True)

  ptitle = GliderPlot.add_title(cruiseid='',
                    fileid=filein.split('/')[-1],
                    castid=diveNum,
                    castdate=data_time[0],
                    lat=lat,
                    lon=lon)

  t = fig.suptitle(ptitle)
  t.set_y(1.06)
  DefaultSize = fig.get_size_inches()
  fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )

  plt.savefig('images/dive'+diveNum+'/dive'+diveNum+'_rollvtime.png', bbox_inches='tight', dpi = (300))
  plt.close()