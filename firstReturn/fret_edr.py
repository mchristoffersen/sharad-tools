# script finds first return from radargram per method in Grima et al., 2012.
# this will run through all .img radargrams in directory.
# designed to run on directory structured like the PDS.
# author: Brandon S. Tober
# created: 30January2018
# updated: 23Oct2018

import os,sys
from PIL import Image
import math
import numpy as np
import scipy.misc
import time
import matplotlib.pyplot as plt

def main():
    
    # set path of directory
    #path = '/disk/qnap-2/MARS/orig/supl/SHARAD/EDR/hebrus_valles_sn/'
    path = '/media/anomalocaris/Swaps/MARS/code/sharad-tools/firstReturn/fret_test/EDR/'
    print('\n----------------------------------------------------------------')

    # keep count of the number of rgrams processed
    count = 0       

    t0 = time.time()    # start time
    for root, dirs, files in os.walk(path + 'data/rgram/'):
        for file in files:
            if file.endswith('amp.npy'):
                file_name = file.rstrip('_amp.npy)')
                if (not os.path.isfile(path + 'out/geom/' + file_name + '_geom2.csv')):
                    print('\nComputing first return for observation: ' + file_name + '\n')
                    imarray = np.load(path + 'data/rgram/' + file)

                    #imarray = imarray[:,0:100:1]	# decrease the imarray to make testing faster

                    (r,c) = imarray.shape   
                    C = np.empty((r,c))	# create empty criteria array to localize surface echo for each trace
                    gradient = np.gradient(imarray, axis = 0) # find gradient of each trace in RGRAM

                    # criteria for surface echo - indicator is Pt * dPt-1/dt, 
                    # where P is the signal energy applied on each grame sample (t)
                    # Indicator weights energy of a sample by the derivative preceding it

                    # vectorized criteria calculation
                    C[100:r,:] = imarray[100:r,:]*gradient[99:r-1,:]   
                    
                    # find indices of max critera seletor for each column
                    C_max_ind = np.argmax(C, axis = 0)	
                    maxAmp = np.argmax(imarray, axis = 0) # also find the max power (or amplitude) in each trace to compare with fret algorithm
                    
                    # scale image array by max pixel to create jpg output with fret index
                    dB = 10 * np.log10(imarray / .01)
                    imarrayScale = ((dB / np.amax(dB)) * 255)
                    imarrayScale[ np.where(imarrayScale > 50) ] = 255
                    fret_index = np.zeros((r,c,3), 'uint8')	# create empty fret index and power arrays
                    fret_db = np.empty((c,1))

                    # open geom nav file for rgram to append surface echo power to each trace                
                    nav_file = np.genfromtxt(path + 'data/geom/' + file_name + '_geom.csv', delimiter = ',', dtype = str)

                    #nav_file = nav_file[0:100:1,:]	# decrease the imarray to make testing faster 

                    # create fret index image - show scaled radargram as base
                    fret_index[:,:,0] = fret_index[:,:,1] = fret_index[:,:,2] = imarrayScale[:,:]

                    # indicate max power along track as red
                    fret_index[maxAmp, np.arange(c),0:2] = 0
                    fret_index[maxAmp, np.arange(c),0] = 255  

                    # make index given by fret algorithm yellow
                    fret_index[C_max_ind, np.arange(c),0] = fret_index[C_max_ind, np.arange(c),1] = 255 
                    fret_index[C_max_ind, np.arange(c),2] = 0

                    # record power in dB for data given by fret algorithm
                    fret_amp = imarray[C_max_ind, np.arange(c)]
                    fret_db = 20 * (np.reshape((np.log10(fret_amp)),(c,1)))

                    # append fret values to geom.tab file. this should be the 6th column
                    # if fret has already been run and it is being re-run, overwrite 6th column with new fret values
                    if nav_file.shape[1] == 5:
                        nav_file = np.append(nav_file, fret_db, 1)

                    else:
                        nav_file[:,6] = fret_db[:,0]
                        
                    np.savetxt(path + 'out/geom/' + file_name + '_geom2.csv', nav_file, delimiter = ',', newline = '\n', fmt= '%s')
                    np.savetxt(path + 'out/fret/' + file_name + '_fret_db.txt', fret_db, delimiter=',', newline = '\n', comments = '', header = 'PDB', fmt='%.8f')



                    try:
                        fret_array = Image.fromarray(fret_index[:,::32], 'RGB') # downsample by taking every 32nd trace for output fret image
                        scipy.misc.imsave(path + 'out/fret/' + file_name + '_fret.jpg', fret_array)
                    except Exception as err:
                        print(err)
                    # update the counter to keep track of lines processed
                    count += 1
                    print('First return processing of rgram #' + str(count) + '; ' + file + ' done!')
                else:
                    print('\nFirst-return processing of observation' + file_name + ' already completed! Moving to next line!')

    t1 = time.time()    # end time
    print('\n----------Total Runtime: ' + str((t1 - t0)/60) + ' minutes----------')

# call the main function
main()
        
