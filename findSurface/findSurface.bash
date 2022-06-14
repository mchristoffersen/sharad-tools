#!/bin/bash

# Wrapper for findSurface.py
#
# Written by Stefano Nerozzi, last edit 09-Jun-2022
#
# To run this script:
# ./findSurface.bash -a <study area name> -w <window size> -s <smoothing width> -l <profile list> -r <PDS .IMG dir path> -n <nav file dir path> -f <seisware_flag> -c <number of cpu>
#
# Read instruction file for detailed explanations

if [ ! ${1} ]; then
  echo "Fatal error! You didn't read the README, did you?"
  exit 0
fi

while getopts ":a:w:s:l:r:n:f:c:" opt; do
  case $opt in
    a)
      study_area="$OPTARG"
      ;;
    w)
      window_size="$OPTARG"
      ;;
    s)
      smoothing_width="$OPTARG"
      ;;
    l)
      profile_list="$OPTARG"
      ;;
    r)
      rad_dir_path="$OPTARG"
      ;;
    n)
      nav_dir_path="$OPTARG"
      ;;
    f)
      seis_flag="$OPTARG"
      ;;
    c)
      ncpu="$OPTARG"
      ;;
    \?)
      echo "You didn't read the README, did you?"
      exit 1
      ;;
  esac
done

# Check things with user before making disasters
echo
echo "findSurface by Stefano Nerozzi"
echo
echo "Your output will be in: $PWD/${study_area}/"
echo "The window size is: ${window_size} samples"
echo "The smoothing width is: ${smoothing_width} traces"
echo "This script will search for .IMG files in: ${rad_dir_path}"
echo "his script will search for nav files in: ${nav_dir_path}"
echo "You want to use ${ncpu} cpu threads"
if [[ ${seis_flag} == "y"]]; then
  echo "You want a Seisware-digestible output"
fi
echo
read -p "Before proceeding, is this correct? [Y/n] " -r
if [[ $REPLY =~ ^[Nn]$ ]]; then
  echo "Fucking bananas!"
  exit
fi

# The bash magic begins
mkdir -p ${study_area}
while read profile; do
  profile=${profile#*_}  # Extract the profile number after s_ or S_
  rad_path=$(find ${rad_dir_path} -type f -name "*${profile}_RGRAM.IMG")
  nav_path=$(find ${nav_dir_path} -type f -name "*${profile}_geom_nadir.csv")
  if [[ -z "${rad_path}" ]]; then
    echo "Warning: Radagram ${profile} is missing" | tee -a ${study_area}/log
  elif [[ -z "${nav_path}" ]]; then
    echo "Warning: simc nav ${profile} is missing" | tee -a ${study_area}/log
  else
    echo "Preparing ${profile}..."  | tee -a ${study_area}/log
    echo "python findSurface.py ${study_area} ${window_size} ${smoothing_width} ${rad_path} ${nav_path} ${seis_flag} | tee -a ${study_area}/log" >> tmp_command_list
  fi
done < ${profile_list}

# Use GNU Parallel to run the Python
parallel -j ${ncpu} --no-notice < tmp_command_list

# Cleanup
rm -f tmp_command_list

echo "All done! Everything is in: $PWD/${study_area}/"
