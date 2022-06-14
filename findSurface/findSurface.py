import os,sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

'''
Script to ingest a simc nadir nav file and refine the surface reflector sample location by looking for the max power return.
The output format is identical to the simc nav file.
Note: the sample location won't always correspond to the nadir return.

python findSurface.py [study_area] [window_size] [smoothing_width] [rad_path] [nav_path]

[study_area]: name of the study area, no spaces
[window_size]: desired window size (# of samples), centered on the simc predicted nadir surface return (20-30 are good values)
[smoothing_width]: desired smoothing window width (10-20 are good values)
[rad_path]: path to an archive of radargrams in the PDS .IMG format (e.g., S_01294501_RGRAM.IMG)
[nav_path]: path to the simc-produced nadir nav files (e.g., s_01294501_geom_nadir.csv)

Author: Stefano Nerozzi
Created: 08/Jun/2022
Updated: 10/Jun/2022
'''

# Read and set up arguments
study_area = sys.argv[1]
win_init = int(sys.argv[2])
mavg_size = int(sys.argv[3])
rad_path = sys.argv[4]
nav_path = sys.argv[5]
seis_flag = sys.argv[6]


# Initialize some constants and parameters
r = 3600  # Rows = samples in a trace
c = 0  # Columns = Traces in a radargram
profile = rad_path.split('/')[-1]  # Extract file name
profile = profile.split('_')[1]  # Extract profile number
win_final = win_init  # Initialize second pass window size


# Read the radargram
data = np.fromfile(rad_path, dtype="float32")
c = len(data)//r  # Calculate number of traces
data[data <= 0] = 1e-10  # Turn 0 or negative values into very tiny ones
data = np.reshape(data, (r, c))  # Reshape data into a typical radargram
data_dB = 10 * np.log10(data)  # Change data scale from linear to dB


# Read the simc nav file
nav_data = pd.read_csv(nav_path, sep = ',')  # Read Lat, Lon, predicted nadir surface location from simc nav output file
nad_sample = nav_data['sample'].astype('int')  # Get predicted nadir sample number
nad_sample[nad_sample < 0] = 1800  # Place negative sample numbers into the middle of the radargram


# Find max power surface return near predicted nadir location
sample_maxp_init = np.zeros(c).astype('int')  # Initialize max power sample location array, initial pass
sample_maxp_smooth = np.zeros(c).astype('int')  # Initialize max power sample location array, smoothed by moving avg
sample_maxp_final = np.zeros(c).astype('int')  # Initialize max power sample location array, final pass


try:
    for i in range(c):  # Cycle through every trace
        if (nad_sample[i] - int(win_init / 2) < 0):  # Case where surface is near the top of the radargram
            sample_maxp_init[i] = np.argmax(data_dB[0 : (nad_sample[i] + int(win_init / 2)),i], axis = 0)
        elif (nad_sample[i] + int(win_init / 2) > r):  # Case where surface is near the bottom of the radargram
            sample_maxp_init[i] = np.argmax(data_dB[(nad_sample[i] - int(win_init / 2)) : r,i], axis = 0)
        else: # Case where window does not reach top or bottom of the radargram
            sample_maxp_init[i] = np.argmax(data_dB[(nad_sample[i] - int(win_init / 2)) : (nad_sample[i] + int(win_init / 2)),i], axis = 0)
        sample_maxp_init[i] = int(nad_sample[i] + sample_maxp_init[i] - (win_init / 2))  # Find actual location of max power samples

    sample_maxp_smooth = np.convolve(sample_maxp_init, np.ones((mavg_size,))/mavg_size, mode='same').astype(int)  # Moving average to smooth out the jitter
    for i in range(mavg_size//2):  # Correct the first and last mavg_size/2 samples because they were averaged to zeroes
        sample_maxp_smooth[i] = (sample_maxp_smooth[i] * (mavg_size/(mavg_size//2+i))).astype(int)  # First mavg_size/2 samples
        sample_maxp_smooth[(c-i-1)] = (sample_maxp_smooth[(c-i-1)] * (mavg_size/(mavg_size//2+i+1))).astype(int)  # Last mavg_size/2 samples

    win_final = np.abs(nad_sample - sample_maxp_smooth)*2 + mavg_size//2

    for i in range(c):  # Cycle through every trace a second time with a narrow window
        if (nad_sample[i] - int(win_final[i] / 2) < 0):  # Case where surface is near the top of the radargram
            sample_maxp_final[i] = np.argmax(data_dB[0 : (nad_sample[i] + int(win_final[i] / 2)),i], axis = 0)
        elif (nad_sample[i] + int(win_final[i] / 2) > r):  # Case where surface is near the bottom of the radargram
            sample_maxp_final[i] = np.argmax(data_dB[(nad_sample[i] - int(win_final[i] / 2)) : r,i], axis = 0)
        else: # Case where window does not reach top or bottom of the radargram
            sample_maxp_final[i] = np.argmax(data_dB[(nad_sample[i] - int(win_final[i] / 2)) : (nad_sample[i] + int(win_final[i] / 2)),i], axis = 0)
        sample_maxp_final[i] = int(nad_sample[i] + sample_maxp_final[i] - (win_final[i] / 2))  # Find actual location of max power samples

except Exception as err:
    print(err)
    print('Profile ' + profile + ': Fucking bananas!')

nav_data['sample'] = sample_maxp_final  # Substitute sample locations


# Export simc-like nav file with new sample locations
nav_data['lat'] = nav_data['lat'].map(lambda x: '%.6f' % x)  # Keep original float precision because pandas is stupid
nav_data['lon'] = nav_data['lon'].map(lambda x: '%.6f' % x)  # Keep original float precision because pandas is stupid
nav_data['elev_IAU2000'] = nav_data['elev_IAU2000'].map(lambda x: '%.3f' % x)  # Keep original float precision because pandas is stupid
nav_data.to_csv(study_area + '/s_' + profile + '_geom_nadir_maxp.csv', index = False)

# Export Seisware horizon
if (seis_flag == "y"):
    seis_data = pd.DataFrame(index=range(c))  # Create new dataframe with one row for each trace
    seis_data['profile'] = ('s_' + profile)  # Assign the same profile name for each row
    seis_data['trace'] = range(c)  # Write trace number
    seis_data['surf_twt'] = nav_data['sample']* 37.5e-9 *1e4  # Multiply sample by 37.5 ns and then by the 1e4 fake time multiplier for Seisware
    seis_data.to_csv(study_area + '/s_' + profile + '_surf.csv', index = False)


# The following code is for test purposes
'''
noise_floor = np.median(data_dB[:20,:])  # Find a noise floor from median power of first 20 rows
data_dB_scaled = data_dB - noise_floor  # Scale image array by noise floor
maxdB = np.median(np.amax(data_dB_scaled, axis = 0))  # Find a maximum power from median of maximum power of each trace
data_dB_im = data_dB_scaled / maxdB * 255  # Scale image by maximum power and 255 to turn into a grayscale image
data_dB_im[np.where(data_dB_im < 0)] = 0.  # Get rid of negative pixel values
data_dB_im[np.where(data_dB_im > 255)] = 255.  # Get rid of pixel values over 255

imarray = np.zeros((r,c,3), 'uint8')  # Create empty surf index and power arrays
imarray[:,:,0] = imarray[:,:,1] = imarray[:,:,2] = data_dB_im[:,:]  # Add scaled radargram grayscale image as base

# Indicate first pass max power along track as blue
imarray[sample_maxp_init, np.arange(c),0] = 0
imarray[sample_maxp_init, np.arange(c),1] = 0
imarray[sample_maxp_init, np.arange(c),2] = 255

# Indicate second pass max power along track as red
imarray[sample_maxp_final, np.arange(c),0] = 255
imarray[sample_maxp_final, np.arange(c),1] = 0
imarray[sample_maxp_final, np.arange(c),2] = 0

# Indicate nadir position as yellow
imarray[nad_sample, np.arange(c),0] = 255  
imarray[nad_sample, np.arange(c),1] = 255
imarray[nad_sample, np.arange(c),2] = 0

im = Image.fromarray(imarray)
im.save(study_area + "/" + profile +".png")
'''

print("Done processing profile " + profile)
