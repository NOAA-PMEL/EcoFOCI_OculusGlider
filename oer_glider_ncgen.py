#!/usr/bin/env python

"""
 Background:
 --------
 oer_glider_test.py
 
 
 Purpose:
 --------
 
 History:
 --------


"""
import xarray as xa
import argparse

from io_utils import ConfigParserLocal
from calc import aanderaa_corrO2_sal as optode_O2_corr
import io_utils.glider_functions as glider


"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Create Glider NetCDF data')
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

rawdata, data_obj, header_data = glider.get_inst_data(filein, MooringID='oculus_test')

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


# Build xarray dataset
xaData = xa.Dataset({'pressure': (['time'], pressure),
                   'SBE_Temperature': (['time'], SBE_Temperature),
                   'SBE_Salinity': (['time'], SBE_Salinity),
                   'Aand_DO': (['time'], Aand_DO),
                   'Aand_DO_Sat': (['time'], Aand_DO_Sat),
                   'Aand_Temperature': (['time'], rawdata['aa4330.Temp']),
                   'Upward_PAR': (['time'], rawdata['satu.PARuV']),
                   'Downward_PAR': (['time'], rawdata['satd.PARuV']),
                   'Aand_Temperature': (['time'], rawdata['aa4330.Temp']),
                   'Wetlabs_CDOM': (['time'], Wetlabs_CDOM),
                   'Wetlabs_CHL': (['time'], Wetlabs_CHL),
                   'Wetlabs_NTU': (['time'], Wetlabs_NTU)},
                    coords={'time':data_time})

#######################
#
# Data Archive
### Update NetCDF attributes (global/variable)
ncatts_file_path = '/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_AcrobatProcessing/inst_config/spring_test_oculus_nc_atts.yaml'
netcdf_attrs = ConfigParserLocal.get_config(ncatts_file_path,ftype='yaml')

for variable_name in xaData.keys():
    try:
        var_att_update(xaData,variable_name,netcdf_attrs[variable_name])
    except KeyError:
        print "Variable:{var} is not in nc_atts.yaml file.  Attributes wont be updated for it".format(var=variable_name)

### global attributes
for gatts in netcdf_attrs['Global_Attributes']:
    xaData.attrs[gatts] = netcdf_attrs['Global_Attributes'][gatts]

