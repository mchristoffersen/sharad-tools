# sharad-tools #

This repo holds tools for working with SHARAD data. Right now there are three:
 
 ## rangeCompress
 A set of functions to pulse compress Italian EDR data - includes both matlab and python versions
 range_Compress.py script imports various other functions and performs range compression
 
 ## depthAdjust
 A python script to do depth correction on radargrams
 
 ## surfPow
 Extracts surface power from SHARAD radargrams
 nadir module used to find nadir location which can be used for windowing firest return selection
 
 ## psql
 Python scripts for database management of SHARAD EDRs. 
* edrNav_info.py parses EDRs to create csv files for each track with lat, long, sza
* edrNav_DB.txt contains postgresql commands to create table to hold EDR nav information for querying
* edrNav_psql_import.py imports EDR nav csv files to postgresql database
* sharadList_mod.py modifies query list output from postgresql database to match PDS SHARAD filenames
 
 ## firstReturn
 A set of python sripts for extracting the firt return power (reflectivity) from SHARAD tracks -- old
 This has essentially been replaced by surfPow/
