# script finds first return from radargram per method in Grima et al., 2012.
# this will run through all .img radargrams in directory.
# designed to run on directory structured like the PDS.
# author: Brandon S. Tober
# created 30January2018
# updated: 23Oct2018

import os,sys
from PIL import Image
import math
import numpy as np
import scipy.misc
import time

def main():
    
    # set path of directory
    #path = '/disk/qnap-2/MARS/orig/supl/SHARAD/EDR/hebrus_valles_sn/'
    path = '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/supl/SHARAD/EDR/hebrus_valles_sn/'
    print('\n----------------------------------------------------------------')

    # keep count of the number of rgrams processed
    count = 0       

    t0 = time.time()    # start time
    for root, dirs, files in os.walk(path + 'processed/data/rgram/'):
        for file in files:
            if file.endswith('pow.npy'):
                file_name = file.rstrip('_pow.npy)')
                if (not os.path.isfile(path + 'processed/data/geom/' + file_name + '_geom2.csv')):
                    print('\nComputing first return for observation: ' + file_name + '\n')
                    imarray = np.load(path + 'processed/data/rgram/' + file)

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
                    # create empty fret index and power arrays
                    fret_index = np.zeros((r,c))

                    # open geom nav file for rgram to append surface echo power to each trace                
                    nav_file = np.genfromtxt(path + 'processed/data/geom/' + file_name + '_geom.csv', delimiter = ',', dtype = str)

                    #nav_file = nav_file[0:100:1,:]	# decrease the imarray to make testing faster 

                    # vectirized first return array and first return power out
                    # attach max criteria indices for each column to first return array - make white
                    fret_index[C_max_ind, np.arange(c)] = 255    
                    fret_pow = imarray[C_max_ind, np.arange(c)]
                    fret_db = np.reshape((np.log10(fret_pow)*10),(c,1))

                    # append fret values to geom.tab file. this should be the 6th column
                    # if fret has already been run and it is being re-run, overwrite 6th column with new fret values
                    if nav_file.shape[1] == 5:
                        nav_file = np.append(nav_file, fret_db, 1)

                    else:
                        nav_file[:,6] = fret_db[:,0]
                        
                    np.savetxt(path + 'processed/data/geom/' + file_name + '_geom2.csv', nav_file, delimiter = ',', newline = '\n', fmt= '%s')
                    np.savetxt(path + '/processed/data/fret/' + file_name + '_fret_db.txt', fret_db, delimiter=',', newline = '\n', comments = '', header = 'PDB', fmt='%.8f')

                    # convert fret array to image and save
                    # presum data by factor for visualization purposes
                    presumFac = 32
                    presumCols = int(np.ceil(c/presumFac))
                    C_max_ind_presum = np.zeros(presumCols)
                    C_max_ind_presum_int = np.zeros((presumCols),dtype = int)
                    fret_presum = np.zeros((r, presumCols))

                    for _i in range(presumCols - 1):
                        C_max_ind_presum[_i] = int(np.mean(C_max_ind[presumFac*_i:presumFac*(_i+1)]))

                    # account for traces left if number of traces is not divisible by presumFac
                    C_max_ind_presum[-1] = int(np.mean(C_max_ind[presumFac*(_i+1):-1]))

                    C_max_ind_presum_int[:] = C_max_ind_presum[:]
                    fret_presum[C_max_ind_presum_int, np.arange(presumCols)] = 255

                    try:
                        scipy.misc.imsave(path + 'processed/data/fret/' + file_name + '_fret.jpg', fret_presum)
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
        
