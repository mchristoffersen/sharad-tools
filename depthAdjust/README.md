Michael Christoffersen
October 2017

This script does depth correction on SHARAD data using the nadir track 
in cluttergrams. It works by:

(1) Finding the nadir or first return (colored pixel) in each trace of the 
cluttergram and recording it's location


(2) Compressing all of the data below the nadir with the given 
dielectric constant

Usage:

python depthAdj.py [path_to_cluttergam] [path_to_radargram] [dielectric_constant] [output name]

Example:

python nadir_depthadj.py ./sims/UTSIM_1294501000-v1.5-4096-Sim.png ./radargrams/s_01294501_tiff.tif 3.1 1294501_depthadj_31.tif
