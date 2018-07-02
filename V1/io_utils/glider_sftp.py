#!/usr/bin/env python

"""
 Background:
 --------
 glider_sftp.py
 
 
 Purpose:
 --------
 retrieve updated glider data from APL sftp site

 must have approved of the host:key process once before (so connect via command line sftp prior to using this program)

 History:
 --------
 2017-08-10: Bell - add a state file so that not all data has to be redownloaded

"""


import datetime
import pysftp

import ConfigParserLocal

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2017, 07, 26)
__modified__ = datetime.datetime(2017, 07, 26)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'sftp','get data'



sftp_config_file = '../EcoFOCI_config/sftp_config/apl_sftp_oculus.pyini'
sftp_config = ConfigParserLocal.get_config(sftp_config_file,ftype='yaml')
state_file = '../EcoFOCI_config/2017_sg401_south.yaml'
state_config = ConfigParserLocal.get_config(state_file,ftype='yaml')

ncfile_list = [state_config['base_id'] + str(item).zfill(4) for item in range(state_config['startnum'],state_config['endnum'],1)]

if sftp_config['RetrieveAll']:
    with pysftp.Connection(sftp_config['host'], username=sftp_config['user'], password=sftp_config['password']) as sftp:
        sftp.get_d(sftp_config['ftppath'],sftp_config['localpath']) 
else:
    with pysftp.Connection(sftp_config['host'], username=sftp_config['user'], password=sftp_config['password']) as sftp:
        badfile = 0
        sftp.chdir(sftp_config['ftppath'])       # chdir to path in config file
        for ncfile in ncfile_list:
            if sftp.exists('{0}.nc'.format(ncfile)):
                print("Grabbing {0}.nc".format(ncfile)) 
                sftp.get('{0}.nc'.format(ncfile))         # get a remote file
            else:
                print("File {0}.nc does not exist".format(ncfile))
                badfile +=1

            if badfile > 5:
                break
