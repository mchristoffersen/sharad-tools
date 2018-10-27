from PIL import Image
import numpy as np
import sys, scipy.ndimage, warnings

# Michael Christoffersen, October 2017
# Python 2.7

# Usage:
# python nadir_depthadj.py [path_to_cluttergam] [path_to_radargram] [dielectric_constant] [output name]

# Depth correcting software for radargrams.
# Takes in a cluttergram with a nadir trace 
# and an image of the real data. It will find
# the nadir trace (which must be the specified color)
# and adjust the timing of all data below it with
# the specified dielectric constant

# Paths to the cluttergram with nadir track and the data
clut_path = sys.argv[1] #'./UTSIM_1294501000-v1.5-4096-Sim.png'
data_path = sys.argv[2] #'./s_01294501_tiff.tif'
# Color of the nadir trace in the cluttergram
nadir_color = [50,255,255]
# Dielectric constant to adjust with
dc = float(sys.argv[3]) #3.2
# Speed of light used to make cluttergram
ospd = 3e8

print("Nadir color = " + str(nadir_color))
print("Speed of light used in cluttergram = " + str(ospd))
print("Loading images...")
#Open the images with PIL
clut_img = Image.open(clut_path)
data_img = Image.open(data_path)

# Read the image data into arrays
#clut = np.array(clut_img)
clut = scipy.misc.imread(clut_path, flatten=False, mode='RGB')
data = np.array(data_img)

if(clut.shape[1] != data.shape[1]):
	sys.exit("Error: clutter and data lengths do not match (" + str(clut.shape[1]) + ", " + str(data.shape[1]) + ")")

# Make empty array for depth corrected data
adj_data = np.zeros(data.shape)
# Array to hold the nadir position for each trace
nad_loc = np.zeros(len(clut[0])).astype('int16')

# Calculate speed of light with dielectric constant
# spdfrac is used to do the adjusting
nspd = 3e8/(dc**.5)
spdfrac = nspd/ospd

warnings.simplefilter("ignore", UserWarning) # getting rid of a dumb warning

# Find the location of the first return in the cluttergram using the nadir_color
# variable.
print("Finding nadir location in cluttergram...")
match0 = (clut[:,:,0] == nadir_color[0])
match1 = (clut[:,:,1] == nadir_color[1])
match2 = (clut[:,:,2] == nadir_color[2])
matchall = np.logical_and(match0, match1, match2)
nad_loc = np.where(matchall)
					
# This loops through the data, it copies everything above the nadir to 
# the new array with no change and compresses everything below the nadir
# with the scipy zoom function, then copies it over to the new radargram
print("Adjusting data...")
dlen = len(data)
dwidth = len(data[0])
for i in range(dwidth):
	sys.stdout.write(str(round(100*float(i)/dwidth))+"%\r") # making the % display
	sys.stdout.flush()
	nloc = nad_loc[0][nad_loc[1] == i][0] # getting the nadir location
	adj_data[0:nloc,i] = data[0:nloc,i] # copying stuff above nadir
	new = scipy.ndimage.zoom(data[nloc:dlen,i],spdfrac) # compressing stuff below
	adj_data[nloc:nloc+len(new),i] = new # then putting it in the new image

print("Writing image file...")
# Some boilerplate to produce a png from the array
adj_data_img = Image.fromarray(adj_data)
if adj_data_img.mode != 'RGB':
    adj_data_img = adj_data_img.convert('RGB')
# Saving the produced image
adj_data_img.save(sys.argv[4])
