# EcoFOCI_OculusGlider - V2

## Background
Purpose is to parse Glider NetCDF files as they come from the glider base station and to provide visualization of the data for scientific discussion.  It is assumed that much of the engineering discussion can be framed around the graphics and information provided by the UW basestation software.

### 2018 Deployment
There are three gliders being deployed for 2018.  Two will be deployed in the Bering Sea and one will be deployed in the Beaufort.   
Priorities will be:
- to make the data available in near realtime via erddap server
- plot the geolocation of each of the three gliders
- to make dive profiles of
    + Temperature
    + Salinity
    + Oxy (% Sat)
    + Chlor-A
    + T/S diagrams for BS
- to make contour profiles (depth v time of each of the above parameters).  Ideally it would be nice if these were "slider driven" on a dynamic web page

### Included instruments (and thus the timebase for each)
aa4330 (oxy) ***other (ERDDAP)***
    + aa4330_O2
    + aa4330_airsat
    + aa4330_temp
    + aa4330_time
    + aanderaa4330_dissolved_oxygen
sbect (T/S/sigma-t/depth) *** Profile_id***
    + ctd_pressure
    + ctd_depth (coordinate axis)
    + conductivity
    + salinity
    + salinity_raw
    + temperature
    + ctd_time
    + sigma-t
    + latitude
    + longitude
wlbb2fl (chlor/turb/scat) ***other (ERDDAP)***
    + wlbb2fl_time (wlbb2fl_results_time?)
    + wlbb2fl_sig470nm
    + wlbb2fl_sig695nm_adjusted
    + wlbb2fl_sig700nm_adjusted
sg_data (lat,lon,depth - glider based parameters)
    + ~~longitude~~ currently on sbe timescale
    + ~~latitude~~ currently on sbe timescale
    + time
PAR - scicon_satpar_satPAR_data_point ***other (ERDDAP)***
    + satPAR_Temp
    + satPAR_time
    + satPAR_PARuV

*** NOTE: *** only CTD timeseries will have explicit depth paramter.  Other parameters will need to be matched in time with no depth parameter

################

Legal Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration (NOAA), or the United States Department of Commerce (DOC). All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. Any claims against the DOC or DOC bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation, or favoring by the DOC. The DOC seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by the DOC or the United States Government.