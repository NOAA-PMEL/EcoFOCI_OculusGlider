#!/usr/bin/env python

"""
 Background:
 --------
 glider_functions.py
 
 
 Purpose:
 --------
 
 History:
 --------


"""

import datetime
from io import BytesIO
import pandas as pd
import numpy as np
import seawater as sw

def get_inst_data(filename, **kwargs):
    r"""

    Parameters
    ----------
    filename : string
        complete path to file to be ingested

    MooringID : string
        Unique MooringID (EcoFOCI format for cross referencing with meta database)

    source : string
        Matches available data sources to determine class instantiation
    kwargs
        Arbitrary keyword arguments to use to initialize source

    Returns
    -------
    Dataset : dictionary of dictionaries
        time : dictionary
            key:    dataindex
            value:  datetime type
        variables : dictionary of dictionaries
            key:    dataindex
            value:  float, int, string (depending on instrument)

    """
    instrument = oculus_rawdata(filename)
    fobj = instrument.get_data(kwargs['MooringID'])
    Dataset = instrument.parse(fobj, **kwargs)
    header_data = instrument.get_header(fobj, **kwargs)

    return Dataset, instrument, header_data

class oculus_rawdata(object):

    names = ['elaps_t_0000','elaps_t','depth','head','pitchAng','rollAng',
    'pitchCtl','rollCtl','vbdCC','rec','GC_phase','sbect.condFreq','sbect.tempFreq',
    'aa4330.O2','aa4330.AirSat','aa4330.Temp','aa4330.CalPhase','aa4330.TCPhase',
    'wlbb2fl.temp','mag.x','mag.y','mag.z','satd.Timer','satd.PARuV','satd.pitch',
    'satd.roll','satd.Temp','satu.Timer','satu.PARuV','satu.pitch',
    'satu.roll','satu.Temp','wlbb2fl.sig470nm','wlbb2fl.sig700nm','wlbb2fl.sig695nm']


    def __init__(self, data_file='test.txt'):
        self.filename = data_file
        self.header_data = {}

    def get_data(self, MooringID=None, **kwargs):
        r"""
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments
        """

        fobj = open(self.filename)
        data = fobj.read()


        buf = data
        return BytesIO(buf.strip())

    def get_header(self,fobj,**kwargs):
        r"""Parse Oculus Data header

        """        
        
        fobj.seek(0)
        for k, line in enumerate(fobj.readlines()):
            line = line.strip()
            
            if ('%version' in line):  
                self.header_data['version'] = line.split()[1]
            elif ('%glider' in line):  
                self.header_data['glider'] = line.split()[1]                
            elif ('%mission' in line):  
                self.header_data['mission'] = line.split()[1]  
            elif ('%dive' in line):  
                self.header_data['dive'] = line.split()[1]  
            elif ('%basestation_version' in line):  
                self.header_data['basestation_version'] = line.split()[1]  
            elif ('%start' in line):
                self.header_data['time_start_str'] = "".join(line[1:])  
                self.header_data['time_start'] = datetime.datetime.strptime('2017-' + line.split()[1] + '-' + line.split()[2] + \
                                                                            ' ' + line.split()[4] + ':' + line.split()[5] + ':' + line.split()[6],
                                                                            '%Y-%m-%d %H:%M:%S')
        return self.header_data

    def parse(self, fobj, **kwargs):
        r"""Parse Oculus Data by skipping over header which also has dive number

        """
        fobj.seek(0)
        self.rawdata = pd.read_csv(fobj, delim_whitespace=True, skiprows=8, names=oculus_rawdata.names)

        return self.rawdata

    def castdirection(self):
        """determin index of upcast and downcast - based on reaching max depth"""
        downcast = [0,np.argmax(self.rawdata['depth'])+1]
        upcast = [np.argmax(self.rawdata['depth']),len(self.rawdata['depth'])]

        return (downcast,upcast)

    def elapsedtime2date(self):
        temp_time =  [datetime.timedelta(seconds=x)+self.header_data['time_start'] for x in self.rawdata['elaps_t'] ]
        
        return np.array(temp_time)

    def depth2press(self, lat=0):
        """
        depth is in meters * 100 (aka cm)
        """
        self.pressure = sw.pres(self.rawdata['depth'] / 100., lat)

        return self.pressure

    def sbe_temp(self, coefs=None):
        r"""
        
        ITS-90

        coefs: dictionary
        
        """
        temp_denominator = coefs['g'] + \
                        (coefs['h'] * np.log(coefs['f0'] / self.rawdata['sbect.tempFreq'])) + \
                        (coefs['i'] * np.log(coefs['f0'] / self.rawdata['sbect.tempFreq'])**2.) + \
                        (coefs['j'] * np.log(coefs['f0'] / self.rawdata['sbect.tempFreq'])**3.)

        self.SBE_Temp = 1. / temp_denominator - 273.15

        return self.SBE_Temp

    def sbe_cond(self, coefs=None):
        r"""
        
        PSS-1978

        coefs: dictionary

        """     
        cond_numerator = coefs['g'] + \
                        (coefs['h'] * (self.rawdata['sbect.condFreq']/1000.)**2.) + \
                        (coefs['i'] * (self.rawdata['sbect.condFreq']/1000.)**3.) + \
                        (coefs['j'] * (self.rawdata['sbect.condFreq']/1000.)**4.)

        cond_denominator = 10.0 * (1 + coefs['CTcor']*self.SBE_Temp) + \
                        (coefs['CPcor']*self.pressure)

        return cond_numerator / cond_denominator


    def wetlabs_cdom(self, coefs=None, varname='wlbbfl2.sig460nm'):
        return coefs['ScaleFactor'] * (self.rawdata[varname] - coefs['DarkCounts'])

    def wetlabs_chl(self, coefs=None, varname='wlbbfl2.sig695nm'):
        return coefs['ScaleFactor'] * (self.rawdata[varname] - coefs['DarkCounts'])

    def wetlabs_ntu(self, coefs=None, varname='wlbbfl2.sig700'):
        return coefs['ScaleFactor'] * (self.rawdata[varname] - coefs['DarkCounts'])

def cond2salinity(conductivity=None, temperature=None, pressure=None):
    
    stand_sw_cond = 4.2914 #S*m-1

    condr = conductivity / stand_sw_cond

    return sw.salt(condr, temperature, pressure)
