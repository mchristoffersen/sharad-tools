# wrapper to range compress SHARAD EDRs then calculate surface reflectivity
# inputs - list of SHARAD tracks for which to calculate reflectivity
# ./SHARADreflecitity.sh [number of jobs] [study region] [list_of_tracks.txt]
# BST - 06DEC2019


# $1 is the number of jobs to process in parallel at once
# $2 is the study region name
# $3 is a SHARAD observation or list of observations

###CODE###
# reset bash time counter
SECONDS=0

# create necessary directories
mkdir -p /zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$2/data/rgram/amp
mkdir /zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$2/data/geom
mkdir -p /zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$2/browse/tiff
mkdir -p /zippy/MARS/targ/xtra/SHARAD/EDR/surfPow/$2

echo "Beginning range compression using $1 threads"
echo "Study region: $2"
echo "----------"

/usr/local/parallel/bin/parallel -j$1 python3 rangeCompress/code/python/range_Compress.py $2 :::: $3
echo "Range compression completed"
echo "----------"

find zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/$1/data/rgram/amp/ > rc_out_list.txt
echo "Calculating surface reflectivity"
/usr/local/parallel/bin/parallel -j$1 python3 surfPow/surf_Pow.py $2 :::: rc_out_list.txt
echo "Surface reflectivity calculation completed"
echo "----------"

echo "Removing data files"
rm -r zippy/MARS/targ/SHARAD/EDR/rangeCompress/$1/data/
rm rc_out_list.txt
echo "----------"

# display run time
echo "Runtime: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"