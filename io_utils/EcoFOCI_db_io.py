#!/usr/bin/env python

"""
 Background:
 --------
 EcoFOCI_db_io.py
 
 
 Purpose:
 --------
 Various Routines and Classes to interface with the mysql database that houses EcoFOCI meta data
 
 History:
 --------
 2017-07-28 S.Bell - replace pymsyql with mysql.connector -> provides purepython connection and prepared statements

"""

import mysql.connector
import ConfigParserLocal 
import datetime
import numpy as np

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2017, 7, 28)
__modified__ = datetime.datetime(2017, 7, 28)
__version__  = "0.2.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header','pymysql'

class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        if np.isnan(value):
            return None
        return float(value)

    def _float64_to_mysql(self, value):
        if np.isnan(value):
            return None
        return float(value)

    def _int32_to_mysql(self, value):
        if np.isnan(value):
            return None
        return int(value)

    def _int64_to_mysql(self, value):
        if np.isnan(value):
            return None
        return int(value)

class EcoFOCI_db_oculus(object):
    """Class definitions to access EcoFOCI Mooring Database"""

    def connect_to_DB(self, db_config_file=None, ftype='yaml'):
        """Try to establish database connection

        Parameters
        ----------
        db_config_file : str
            full path to json formatted database config file    

        """
        db_config = ConfigParserLocal.get_config(db_config_file,ftype)
        try:
            self.db = mysql.connector.connect(**db_config)
        except mysql.connector.Error as err:
          """
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
          else:
            print(err)
          """
          print("error - will robinson")
          
        self.db.set_converter_class(NumpyMySQLConverter)

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor(dictionary=True)
        self.prepcursor = self.db.cursor(prepared=True)
        return(self.db,self.cursor)

    def manual_connect_to_DB(self, host='localhost', user='viewer', 
                             password=None, database='ecofoci', port=3306):
        """Try to establish database connection

        Parameters
        ----------
        host : str
            ip or domain name of host
        user : str
            account user
        password : str
            account password
        database : str
            database name to connect to
        port : int
            database port

        """
        db_config = {}     
        db_config['host'] = host
        db_config['user'] = user
        db_config['password'] = password
        db_config['database'] = database
        db_config['port'] = port

        try:
            self.db = mysql.connector.connect(**db_config)
        except:
            print "db error"
            
        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor(dictionary=True)
        self.prepcursor = self.db.cursor(prepared=True)
        return(self.db,self.cursor)

    def read_profile(self, table=None, divenum=None, castdirection='None', param=None, result_index='depth', verbose=False):
        
        if castdirection in ['all']:
          sql = ("SELECT id,{parameter},depth,time from `{table}` WHERE `divenum`= '{divenum}'  ORDER BY `id` DESC ").format(table=table, 
                                                                                                                             divenum=divenum,
                                                                                                                             parameter=param,
                                                                                                                             cast_dir=castdirection)
        else:
          sql = ("SELECT id,{parameter},depth,time from `{table}` WHERE `divenum`= '{divenum}' and `castdirection` LIKE '%{cast_dir}%' ORDER BY `id` DESC ").format(table=table, 
                                                                                                                                             divenum=divenum,
                                                                                                                                             parameter=param,
                                                                                                                                             cast_dir=castdirection)

        if verbose:
            print sql

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row[result_index]] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
            return (result_dic)
        except:
            print "Error: unable to fetch data"



    def read_location(self, table=None, param=None, dive_range=None, verbose=False):
        
        sql = ("SELECT divenum,{parameter},time from `{table}` WHERE divenum BETWEEN {dive_start} AND {dive_end} GROUP BY divenum ").format(table=table,
                                                                                              dive_start=dive_range[0],
                                                                                              dive_end=dive_range[1],
                                                                                              parameter=",".join(param))

        if verbose:
            print sql

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row['divenum']] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
            return (result_dic)
        except:
            print "Error: unable to fetch data"

    def read_ave_lat(self, table=None, divenum=None, castdirection=None, param=None, verbose=False):
        
        sql = ("SELECT {parameter},depth,time,latitude from `{table}` WHERE `divenum`= '{divenum}' and `castdirection`='{cast_dir}' ORDER BY `id` DESC ").format(table=table, 
                                                                                                                                             divenum=divenum,
                                                                                                                                             parameter=param,
                                                                                                                                             cast_dir=castdirection)
               
        """
        sql = ("SELECT FORMAT(latitude, 3) AS latitude ,{parameter} from `{table}` WHERE divenum BETWEEN {dive_start} AND {dive_end} GROUP BY 1 ").format(table=table,
                                                                                              dive_start=dive_range[0],
                                                                                              dive_end=dive_range[1],
                                                                                              parameter=",".join("avg({param}) AS {param}".format(param=param)))
        """
        if verbose:
            print sql

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row['depth']] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
            return (result_dic)
        except:
            print "Error: unable to fetch data"

    def count(self, table=None, start=None, end=None, verbose=False):
        sql = ("SELECT count(*) FROM (SELECT * FROM `{table}` where `divenum` between"
               " {start} and {end} group by `divenum`) as temp").format(table=table, start=start, end=end)

        if verbose:
            print sql   

        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            # Get column names
            rowid = {}
            counter = 0
            for i in self.cursor.description:
                rowid[i[0]] = counter
                counter = counter +1 
            #print rowid
            # Fetch all the rows in a list of lists.
            results = self.cursor.fetchall()
            return results[0]['count(*)']
        except:
            print "Error: unable to fetch data"

    def add_to_DB(self,table=None,**kwargs):
        """
        CREATE TABLE `2017_beringsea` (
          `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
          `latitude` float DEFAULT NULL,
          `longitude` float DEFAULT NULL,
          `salinity` float DEFAULT NULL,
          `temperature` float DEFAULT NULL,
          `do_sat` float DEFAULT NULL,
          `do_conc` float DEFAULT NULL,
          `470nm` float DEFAULT NULL,
          `up_par` float DEFAULT NULL,
          `down_par` float DEFAULT NULL,
          `sigma_t` float DEFAULT NULL,
          `695nm` float DEFAULT NULL,
          `700nm` float DEFAULT NULL,
          `time` datetime DEFAULT NULL,
          `depth` float DEFAULT NULL,
          `divenum` int(11) DEFAULT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        insert_stmt = "INSERT INTO {table} ({columns}) VALUES ({datapts})".format(
            table=table,
            columns= ','.join(kwargs.keys()),
            datapts=','.join(['?']*len(kwargs.keys())))
        data = (kwargs.values())
        try:
           # Execute the SQL command
           self.prepcursor.execute(insert_stmt,tuple(data))
           self.db.commit()
        except mysql.connector.Error as err:
           print err
           # Rollback in case there is any error
           print "No Bueno"
           print "Failed insert ###" + insert_stmt + "###"
           print tuple(data)

    def position2geojson(self, table=None, verbose=False):
        sql = ("SELECT latitude,longitude,divenum FROM `{table}` group by `divenum`").format(table=table)

        if verbose:
            print sql

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row['divenum']] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
            return (result_dic)
        except:
            print "Error: unable to fetch data"

    def divenum_check(self,table=None,divenum=None):
        sql = ("SELECT 1 FROM `{table}` WHERE divenum = {divenum}").format(table=table,divenum=divenum)

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row['1']] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
            return (result_dic)
        except:
            print "Error: unable to fetch data"

    def to_sql(self,sql=None):
        try:
           # Execute the SQL command
           self.prepcursor.execute(sql)
           self.db.commit()
        except mysql.connector.Error as err:
           print err
           # Rollback in case there is any error
           print "No Bueno"
           print "Failed update ###" + sql + "###"

    def close(self):
        """close database"""
        self.prepcursor.close()
        self.cursor.close()
        self.db.close()

