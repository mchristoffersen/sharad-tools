#!/bin/bash

# Tool to merge cluttersims and PDS radargrams as layers into a single Photoshop PSD file {Stefano Nerozzi, 14-Feb-2022}
#
# ./radsim2PDS.bash [number of parallel jobs] [path to list of profiles] [path to profiles] [path to sims] [name of output folder]
# 
# The list of profiles uses the PDS file naming format, i.e. s_01294501
# PDS radargrams are in the format s_01294501.tiff
# Cluttersims are in the format S_01294501_geom_combinedAdj.png
# Needs GNU Parallel and ImageMagick

# Read arguments
jobs=${1}
list=${2}
rad_dir=${3}
sim_dir=${4}
out_dir=${5}

# Create output directory
mkdir ${out_dir}
cd ${out_dir}

# Warn the user that some bash magic is about to happen! Scripts that generate scripts!
echo "Preparing paths and commands"

# Let the magic begin!
while read line; do
   # This extracts the observation number, here called "prefix"
   profile=${line}
   prefix=${profile:3:10} # Keep only characters 1 to 9, e.g. "1294501" from "s_01294501"
   prefix=$(echo ${prefix}) # This is to clean up the prefix a little bit  

   # This defines the name of the original (input) radargram and cluttersim files
   oldrad="${rad_dir}/s_0${prefix}_tiff.tif"
   oldsim="${sim_dir}/S_0${prefix}_geom_combinedAdj.png"

   # This defines the name of the new (temporary) radargram and cluttersim files, see below
   newrad="${prefix}_rad.png"
   newsim="${prefix}_sim.png"
   
   # The input files need some editing to work properly during the merge, this generates a couple of temporary PNG files
   # Also, cropping to reduce file sizes, because currently ImageMagick can't compress PSDs. Currently, it doesn't crop anything.
   # It's in the format x[heigth]+[x-position]+[y-position]. For example, x1000+0+2150 works well for certain NPLD profiles.
   comm1="magick convert ${oldsim} -crop x3600+0+0 -define png:color-type=2 ${newsim}"
   comm2="magick convert ${oldrad} -crop x3600+0+0 -define png:color-type=2 ${newrad}"

   # This merges the two temporary files as layers inside the final PSD file
   comm3="magick convert \( -page +0+0 -label "radargram" ${newrad} -background none -mosaic -set colorspace RGB \) \( -page +0+0 -label "clutter" ${newsim} -background none -mosaic -set colorspace RGB \) \( -clone 0--1 -background none -mosaic \) -alpha Off -reverse ${prefix}.psd"
   
   # The temporary files are not needed anymore
   comm4="rm ${newrad} ${newsim}"

   # Insert a command to inform the user on the processing progress
   comm5="echo \"Done processing ${prefix}\""

   # Put all the commands into one file that will be read later by GNU Parallel
   echo "${comm1}; ${comm2}; ${comm3}; ${comm4}; ${comm5}" >> commands.txt

done < $list

# Warn the user that the bash magic is about to be executed!
echo "Converting and merging images"

# Very simple parallel command: it runs the commands defined above in n parallel jobs
parallel -j ${jobs} :::: commands.txt

# Delete all proof of the bash magic
rm commands.txt

# Inform the user that the bash magic is over
echo "Done!"
