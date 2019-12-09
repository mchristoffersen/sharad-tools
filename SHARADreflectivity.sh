# wrapper to range compress SHARAD EDRs then calculate surface reflectivity
# inputs - list of SHARAD tracks for which to calculate reflectivity
# ./SHARADreflecitity list_of_tracks.txt
# BST - 06DEC2019


# $1 is the number of tracks to process in parallel at once
# $2 is the study region name
# $3 is a SHARAD observation or list of observations

###CODE###
# reset bash time counter
SECONDS=0

echo "Beginning range compression of using $1 threads"
/usr/local/parallel/bin/parallel -j$1 python3 rangeCompress/code/python/range_Compress.py $2 :::: $3
echo "Range compression completed"

find zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$1/data/rgram/amp/ > rc_out_list.txt

echo "Calculating surface reflectivity"
/usr/local/parallel/bin/parallel -j$1 python3 surfPow/surf_Pow.py $1 :::: rc_out_list.txt
echo "Surface reflectivity calculation completed"

echo "Removing data files"
rm -r zippy/MARS/targ/SHARAD/EDR/rangeCompress/$1/data/rgram/

# display run time
echo "Runtime: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"
