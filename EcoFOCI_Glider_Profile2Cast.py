"""

 Background:
 --------
 EcoFOCI_Glider_Profile2Cast.py
 
 Purpose:
 --------
 Subset Oculus Glider Data from downcast/upcast dives to singel location cast profiles.

 The cast profiles may be created with one of the following three assumptions:
    - downcast only, gridded to 1m bins, geolocation as last good surface point or linear
        interpolation if no surface point
    - upcast only, gridded to 1m bins, geolocation of first good surface point or linear 
        interpolation if no surface point
    - hybrid, gridded to 1m bins, geolocation of last good surface point or linear interpolation 
        if no surface point.  **This is used to address salinity spikes in sharp interfaces**

 Variables kept: Temp, Salinity, Flourometry, PAR (u,d)

 History:
 --------

"""

#System Stack
import os
import argparse

#Science Stack
import numpy as np
import pandas as pd
import xarray as xa

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt


###

plt.style.use('seaborn-ticks')
mpl.rcParams['axes.grid'] = False
mpl.rcParams['axes.edgecolor'] = 'white'
mpl.rcParams['axes.linewidth'] = 0.25
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['xtick.major.size'] = 2
mpl.rcParams['xtick.minor.size'] = 1
mpl.rcParams['xtick.major.width'] = 0.25
mpl.rcParams['xtick.minor.width'] = 0.25
mpl.rcParams['ytick.major.size'] = 2
mpl.rcParams['ytick.minor.size'] = 1
mpl.rcParams['xtick.major.width'] = 0.25
mpl.rcParams['xtick.minor.width'] = 0.25
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.color'] = 'grey'
mpl.rcParams['xtick.color'] = 'grey'
mpl.rcParams['lines.linewidth'] = 0.5
mpl.rcParams['lines.markersize'] = 2

"""----------------------------- Main -------------------------------------"""

parser = argparse.ArgumentParser(description='Oculus Glider Profile2Cast ')
parser.add_argument('filepath', metavar='filepath', type=str,
    help='path to directory with UW processed glider files')
parser.add_argument('--plots', action="store_true",
    help='include profile and comparison plots as output')

### Load Data
#dives=['0085','0230','0400','0490','0500','0510','1000','1100','1500']

dives = [f for f in os.listdir(args.filepath) if f.endswith('.nc')]

for divenum in dives:
    fn = 'p401'+divenum+'.nc'
    #fn = divenum
    print fn
    
    try:
        xdf = xa.open_dataset(path+fn,decode_cf=False)
        xdf.set_coords(['time','depth','latitude','longitude'],inplace=True)
    except:
        print fn + " unloadable - missing key variable"
        continue
    
    try:
        #%%
        ### find thresholds in cast
        # lower bound to downcast
        # bottom of profile
        # upper bound of upcast
        dtdz_down_thresh = -1
        dtdz_up_thresh = -1
        dtdz = np.gradient(xdf.temperature,xdf.depth)
        
        upper_depth = xdf.depth[dtdz<dtdz_down_thresh][0]
        upper_depth_index = np.where(xdf.depth == upper_depth)[0] - 1 #make shallower by one
        if len(upper_depth_index) >1 :
            upper_depth_index = np.array([upper_depth_index[0]])
        bottom_depth = xdf.depth.max()
        bottom_depth_index = np.where(xdf.depth == bottom_depth)[0]
        lower_depth = xdf.depth[bottom_depth_index[0]:][dtdz[bottom_depth_index[0]:]<dtdz_up_thresh][0]
        lower_depth_index = np.where(xdf.depth == lower_depth)[0] - 1 #make deeper by one
        
        downcast_trans = np.where((xdf.depth[0:bottom_depth_index[0]+1] >= upper_depth) & (xdf.depth[0:bottom_depth_index[0]+1] <= lower_depth))[0]
        downcast_trans = np.hstack((downcast_trans,[downcast_trans.max()+1]))
        
        ### Basic Plot with identified points
        if args.plots:
            fig = plt.figure(3, figsize=(4.5,9), facecolor='w', edgecolor='w')
            ax1 = fig.add_subplot(121)
            plt.plot(xdf.temperature,xdf.depth,'r.-')
            plt.plot([xdf.temperature[upper_depth_index],xdf.temperature[bottom_depth_index],xdf.temperature[lower_depth_index]]
                ,[xdf.depth[upper_depth_index],xdf.depth[bottom_depth_index],xdf.depth[lower_depth_index]],'k+')
            ax1.set_ylim([0,np.nanmax(xdf.depth)])
            ax1.invert_yaxis()
            ax1 = fig.add_subplot(122)
            plt.plot(xdf.salinity,xdf.depth,'b.-')
            plt.plot([xdf.salinity[upper_depth_index],xdf.salinity[bottom_depth_index],xdf.salinity[lower_depth_index]]
            ,[xdf.depth[upper_depth_index],xdf.depth[bottom_depth_index],xdf.depth[lower_depth_index]],'k+')
            ax1.set_ylim([0,np.nanmax(xdf.depth)])
            ax1.invert_yaxis()
            t = fig.suptitle('pre correction profile ' + divenum)
            plt.savefig('images/pre_profile_corr_'+divenum+'.png', bbox_inches='tight', dpi = (300))
            plt.close()
        
        """-----------------------------------------------------------------"""
        ### Fill Profile
        # Scale both temperature and salinty to 0->1
        
        def scale(x):
           return (x-min(x)) / (max(x) - min(x))
        
        def rescale(x,y):
            return (1-x)*(y[1] - y[0]) + y[0]
        
        tprime = scale(xdf.temperature[downcast_trans]) # scale
        sprime = rescale(tprime,[xdf.salinity[upper_depth_index][0],xdf.salinity[lower_depth_index][0]])
        """-----------------------------------------------------------------"""
        
        ### Merged Profile w/filling
        if args.plots:
            fig = plt.figure(5, figsize=(4.5,11), facecolor='w', edgecolor='w')
            ax1 = fig.add_subplot(121)
            plt.plot(xdf.temperature[0:upper_depth_index[0]+1],xdf.depth[0:upper_depth_index[0]+1],'r.-')
            plt.plot(xdf.temperature[bottom_depth_index[0]:lower_depth_index[0]+1],xdf.depth[bottom_depth_index[0]:lower_depth_index[0]+1],'m.-')
            plt.plot(xdf.temperature[downcast_trans],xdf.depth[downcast_trans],'k.--')
            ax1.set_ylim([0,np.nanmax(xdf.depth)])
            ax1.invert_yaxis()
            ax1 = fig.add_subplot(122)
            plt.plot(xdf.salinity[0:upper_depth_index[0]+1],xdf.depth[0:upper_depth_index[0]+1],'b.-')
            plt.plot(xdf.salinity[bottom_depth_index[0]:lower_depth_index[0]+1],xdf.depth[bottom_depth_index[0]:lower_depth_index[0]+1],'c.-')
            plt.plot(sprime,xdf.depth[downcast_trans],'k.--')
            ax1.set_xlim([np.nanmin(xdf.salinity),np.nanmax(xdf.salinity)])
            ax1.set_ylim([0,np.nanmax(xdf.depth)])
            ax1.invert_yaxis()
            
            t = fig.suptitle('post correction profile ' + divenum)
            plt.savefig('images/post_profile_corr_'+divenum+'.png', bbox_inches='tight', dpi = (300))
            plt.close()
        
        sal_cor = np.hstack((xdf.salinity[0:upper_depth_index[0]+1],sprime,xdf.salinity[bottom_depth_index[0]:lower_depth_index[0]+1]))
        #sal_cor.shape=(1,1,len(sal_cor),1)
        temp_cor = np.hstack((xdf.temperature[0:upper_depth_index[0]+1],xdf.temperature[downcast_trans],xdf.temperature[bottom_depth_index[0]:lower_depth_index[0]+1]))
        #temp_cor.shape=(1,1,len(temp_cor),1)
        press_cor = np.hstack((xdf.depth[0:upper_depth_index[0]+1],xdf.depth[downcast_trans],xdf.depth[bottom_depth_index[0]:lower_depth_index[0]+1]))
        pdfa = pd.DataFrame(np.stack((sal_cor,temp_cor,press_cor)).T, columns=['Salinity','Temperature','Pressure'])        
        pdfa.set_index('Pressure', inplace=True)
        pdfa.sort_index(inplace=True)
        
        xdfa = xa.Dataset(pdfa,coords={'latitude':xdf.latitude[0],'longitude':xdf.longitude[0],'time':xdf.time[0]})
        
        xdfa.to_netcdf('data/'+fn)
        print fn + " successfully adjusted"
    except:
        ### Basic Plot
        if args.plots:
            fig = plt.figure(1, figsize=(4.5,11), facecolor='w', edgecolor='w')
            ax1 = fig.add_subplot(121)
            plt.plot(xdf.temperature,xdf.depth,'r.-')
            ax1.set_ylim([0,np.nanmax(xdf.depth)])
            ax1.invert_yaxis()
            ax1 = fig.add_subplot(122)
            plt.plot(xdf.salinity,xdf.depth,'b.-')
            ax1.set_xlim([np.nanmin(xdf.salinity),np.nanmax(xdf.salinity)])
            ax1.set_ylim([0,np.nanmax(xdf.depth)])
            ax1.invert_yaxis()
            t = fig.suptitle('basic profile ' + divenum)
            plt.savefig('images/basic_profile_'+divenum+'.png', bbox_inches='tight', dpi = (300))
            plt.close()  

        print fn + " not adjusted"
    
    xdf.close()