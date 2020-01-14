#!/bin/bash

# wrapper to extract list of sharad edr's within desired study region

# user prompted for latitude and longitude bounds, as well as a minimum solar zenith angle

# must run as user postgres 

# example run: su postgres ./SHARADedr_nav_query.sh

# if multiple study regions are being investigated, run queries separately then join lists afterwards

# may want to move file from /tmp/ afterwards to /zippy/MARS/targ/xtra/SHARAD/EDR/ - can't do this as user postgres

# BST - 01_08_2020

###VARS###
echo "Enter longitude and latitude bounds in increasing order"
read -p 'longitude 1: ' lon1
read -p 'longitude 2: ' lon2
read -p 'latitude 1: ' lat1
read -p 'latitude 2: ' lat2
echo "----------------------"
echo "Entered coordinates: ($lon1,$lat1), ($lon2,$lat2)"
echo "----------------------"
echo "Enter the minimum desired solar zenith angle for observations"
read -p 'sza_min: ' sza_min
echo "----------------------"
read -p 'output file name (example - sh_bh_bt_tracks1): ' fname

psql -d sharad -c "COPY(SELECT DISTINCT line FROM edr.nav WHERE lon BETWEEN $lon1 
AND $lon2 AND lat BETWEEN $lat1 AND $lat2 AND sza > $sza_min ORDER BY line) TO '/tmp/$fname.csv' WITH CSV DELIMITER ',';"
echo "----------------------"

# modify the list to match PDS naming structure
python psql/sharadList_mod.py /tmp/$fname.csv

echo "query results output to: /tmp/$fname.csv"