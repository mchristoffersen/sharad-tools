#!/bin/bash

# wrapper to range compress SHARAD EDRs then calculate surface reflectivity

# run in conda py3 environment - conda activate py3

# inputs - list of SHARAD tracks for which to calculate reflectivity

# ./SHARADreflecitity.sh [number of jobs] [study region] [list_of_tracks.txt]

#   -v|--v|--ve|--ver|--verb|--verbo|--verbos|--verbose sets the verbose setting to true - print statements executed in python scripts
#   $1 is the number of jobs to process in parallel at once
#   $2 is the study region name - this should be the same name used for this roi's postgres database
#   $3 is a SHARAD observation or list of observations

# BST - 01_03_2020

###VARS###
# reset bash time counter
SECONDS=0
verbose=0
# verbose flag
case "$1" in
-v|--v|--ve|--ver|--verb|--verbo|--verbos|--verbose)
    verbose=1
    shift ;;
esac
DATE=$(date +"%m_%d_%Y")
NUMTRACKS=$(wc -l < $3)
source reflectivity_config.txt

##CODE###
echo "----------------------------------------------------------------"
echo "Study region: $2"
echo "Number of threads: $1"
echo "Number of tracks to process: $NUMTRACKS"
echo "Verbose: $verbose"
echo "----------------------------------------------------------------"
echo "Beginning range compression"
echo "Chirp type: $CHIRP"
echo "Stacking factor: $STACKFAC"
echo "Beta: $BETA"
echo "----------------------------------------------------------------"

cd /zippy/MARS/code/supl/SHARAD/sharad-tools/rangeCompress/code/python

/usr/bin/parallel -j$1 python3 range_Compress.py $verbose $2 $CHIRP $BETA $STACKFAC :::: $3

echo "Range compression completed"
echo "----------------------------------------------------------------"

cd /zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$2/data/rgram/amp

# get list of range compressed files for input to surface power script
find . -name "*.npy" -exec basename \{} \; > /zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$2/rc_list_$DATE.txt

cd /zippy/MARS/code/supl/SHARAD/sharad-tools

echo "Calculating surface reflectivity"
echo "Surface type: $SURFTYPE"
echo "Window: $WINDOW"
echo "----------------------------------------------------------------"
/usr/bin/parallel -j$1 python3 surfPow/surf_Pow.py $verbose $2 $SURFTYPE $WINDOW :::: /zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$2/rc_list_$DATE.txt
echo "Surface reflectivity calculation completed"
echo "----------------------------------------------------------------"

echo "Removing data files"
rm -r /zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$2/data/
rm -r /zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$2/browse/

# make/append readme to show that range compression was completed on said date
echo "$2 range compression completed on $DATE" >> /zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$2/README.txt
echo "----------------------------------------------------------------"

echo "Adding surface reflectivity measurements to postgres database"

python3 psql/sref/sref_psql_import.py $verbose $2

echo "----------------------------------------------------------------"

# display run time
echo "Total Runtime: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"
echo "----------------------------------------------------------------"