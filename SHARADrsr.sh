#!/bin/bash
# wrapper to run radar statistical recon. on SHARAD data
# inputs - SHARAD surface reflectivity
# ./SHARADrsr.sh list_of_tracks.txt
# BST - 02JAN2020


# $1 is the study region name
# $2 is the number of cores to use to process each track
# $3 is the window size for rsr
# $4 is the step size for rsr
# $5 is a SHARAD surface reflectivity data file, or list of files - geom data with surface reclectivity

###CODE###
# reset bash time counter
SECONDS=0

# create necessary directories
mkdir -p /zippy/MARS/targ/xtra/SHARAD/rsr/$1

cd /zippy/MARS/code/xtra/

echo "Beginning RSR"
echo "----------"
echo "Study region: $1"
echo "Number of cores: $2"
echo "Window size: $3"
echo "Step size: $4"
echo "----------"
/usr/local/parallel/bin/parallel -j1 python -m rsr.main $1 $2 $3 $4 :::: $5
echo "RSR completed"
echo "----------"
# display run time
echo "Runtime: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"