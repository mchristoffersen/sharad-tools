#!/bin/bash
# wrapper to run radar statistical recon. on SHARAD data
# run in conda rsr environment - conda activate rsr
# inputs - SHARAD surface reflectivity
# ./SHARADrsr.sh list_of_tracks.txt
# BST - 02JAN2020

#   -v|--v|--ve|--ver|--verb|--verbo|--verbos|--verbose sets the verbose setting to true - print statements executed in python scripts
# $1 is the study region name - this should be the same name used for this roi's postgres database
# $2 is the number of cores to use to process each track
# $3 is the window size for rsr
# $4 is the step size for rsr
# $5 is a SHARAD surface reflectivity data file, or list of files - geom data with surface reclectivity

# example postgres query to get region sref:
#   COPY(SELECT * FROM edr.sref WHERE roi = 'fuckingBananas' ORDER BY line,trace) to '/tmp/fuckingBananas_sref.csv' WITH (FORMAT CSV, HEADER);

verbose=0
# verbose flag
case "$1" in
-v|--v|--ve|--ver|--verb|--verbo|--verbos|--verbose)
    verbose=1
    shift ;;
esac
###CODE###
# reset bash time counter
SECONDS=0

cd /zippy/MARS/code/xtra/

echo "Beginning RSR"
echo "----------------------------------------------------------------"
echo "Study region: $1"
echo "Number of cores: $2"
echo "Window size: $3"
echo "Step size: $4"
echo "Verbose: $verbose"
echo "----------------------------------------------------------------"
python -m rsr.main $verbose $1 $2 $3 $4
echo "RSR completed"
echo "----------------------------------------------------------------"
echo "Adding surface reflectivity measurements to postgres database"

cd /zippy/MARS/code/supl/SHARAD/sharad-tools/
python3 psql/rsr/rsr_psql_import.py $verbose $1
echo "----------------------------------------------------------------"
# display run time
echo "Runtime: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"