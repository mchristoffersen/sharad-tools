# import necessary libraries
import os,sys
from PIL import Image
import math
import numpy as np
import scipy.misc
import time
import matplotlib.pyplot as plt

def main(rgramFile, surf = 'nadir'):
    '''
    script extracts power of surface return from radargram
    surface return can be defined as either first return (fret), nadir return, or 
    the max power return - return from which most radar energy penetrates surface (max)
    this will run through all .img radargrams in directory.
    designed to run on directory structured like PDS.

    author: Brandon S. Tober
    created: 30January2018
    updated: 21Feb019
    '''
    t0 = time.time()                                                                                                    # start time
    print('--------------------------------')
    print(rgramName)
    print('--------------------------------')

    imarray = np.load(rgramFile)

    # imarray = imarray[:,0:100:1]	                                                                                    # decrease the imarray to make testing faster

    (r,c) = imarray.shape   
    C = np.empty((r,c))	                                                                                                # create empty criteria array to localize surface echo for each trace

    if surf == 'nadir':

    elif surf == 'max':
        print('Code not set up to handle max power return as of yet - BT')
        sys.exit()

    elif surf == 'fret':
        '''       
        criteria for surface echo - indicator is Pt * dPt-1/dt, 
        where P is the signal energy applied on each grame sample (t).
        Indicator weights energy of a sample by the derivative preceding it
        '''

        gradient = np.gradient(imarray, axis = 0)                                                                           # find gradient of each trace in RGRAM

        C[100:r,:] = imarray[100:r,:]*gradient[99:r-1,:]                                                                    # vectorized criteria calculation
        
        C_max_ind = np.argmax(C, axis = 0)	                                                                                # find indices of max critera seletor for each column

    maxAmp = np.argmax(imarray, axis = 0)                                                                                   # find max power (or amplitude) in each trace to compare with fret algorithm
    
    dB = 10 * np.log10(imarray / .01)                                                                                       # scale image array by max pixel to create jpg output with fret index

    imarrayScale = ((dB / np.amax(dB)) * 255)
    imarrayScale[ np.where(imarrayScale > 50) ] = 255
    fret_index = np.zeros((r,c,3), 'uint8')	                                                                                # create empty fret index and power arrays
    fret_db = np.empty((c,1))

    nav_file = np.genfromtxt(data_path + 'data/geom/' + file_name + '_geom.csv', delimiter = ',', dtype = str)              # open geom nav file for rgram to append surface echo power to each trace                

    # nav_file = nav_file[0:100:1,:]	                                                                                        # decrease the imarray to make testing faster 

    fret_index[:,:,0] = fret_index[:,:,1] = fret_index[:,:,2] = imarrayScale[:,:]                                           # create fret index image - show scaled radargram as base
    
    fret_index[maxAmp, np.arange(c),0:2] = 0                                                                                # indicate max power along track as red
    fret_index[maxAmp, np.arange(c),0] = 255  

    fret_index[C_max_ind, np.arange(c),0] = fret_index[C_max_ind, np.arange(c),1] = 255                                     # make index given by fret algorithm yellow
    fret_index[C_max_ind, np.arange(c),2] = 0
    
    fret_amp = imarray[C_max_ind, np.arange(c)]                                                                             # record power in dB for data given by fret algorithm
    fret_db = 20 * (np.reshape((np.log10(fret_amp)),(c,1)))

    if nav_file.shape[1] == 5:                                                                                              # append fret values to geom.tab file. this should be the 6th column
        nav_file = np.append(nav_file, fret_db, 1)

    else:                                                                                                                   # if surfPow with specified surf has already been run and it is being re-run, overwrite 6th column with new pow values
        nav_file[:,6] = fret_db[:,0]
        
    np.savetxt(data_path + 'out/geom/' + file_name + '_geom2.csv', nav_file, delimiter = ',', newline = '\n', fmt= '%s')
    np.savetxt(data_path + 'out/fret/' + file_name + '_fret_db.txt', fret_db, delimiter=',', newline = '\n', comments = '', header = 'PDB', fmt='%.8f')

    try:
        fret_array = Image.fromarray(fret_index[:,::32], 'RGB')                                                             # downsample by taking every 32nd trace for output fret image
        scipy.misc.imsave(data_path + 'out/fret/' + file_name + '_fret.jpg', fret_array)
    except Exception as err:
        print(err)

    t1 = time.time()                                                                                                        # end time
    print('--------------------------------')
    print('Total Runtime: ' + str(round((t1 - t0),4)) + ' seconds')
    print('--------------------------------')
    return

if __name__ == '__main__':
    
    # get correct data paths if depending on current OS
    in_path = '/MARS/orig/supl/SHARAD/EDR/hebrus_valles_sn/'
    out_path = 'MARS/targ/xtra/surfPow/'
    if os.getcwd().split('/')[1] == 'media':
        in_path = '/media/anomalocaris/Swaps' + in_path
        out_path = '/media/anomalocaris/Swaps' + out_path
    elif os.getcwd().split('/')[1] == 'mnt':
        in_path = '/mnt/d' + in_path
        out_path = '/mnt/d' + out_path
    elif os.getcwd().split('/')[1] == 'disk':
        in_path = '/disk/qnap-2/' + in_path
        out_path = '/disk/qnap-2/' + out_path
    else:
        print('Data path not found')
        sys.exit()
   
    rgramFile = sys.argv[1]                                                                                                 # input radargram - range compressed - amplitude output
    rgramFile = in_path + rgramFile                                                                                         # attach input data path to beginning of rgram file name
    fileName = rgramFile.split('_')[0] + '_' + rgramFile.split('_')[1]                                                      # base fileName
    rgramName = fileName[.split('_')[0] + fileName.split('_')[1]                                                            # SHARAD rgram obs. #
    surf = 'nadir'                                                                                                          # define the desired surface pick = [fret,narid,max]
    
    # check if surfPow has already been determined for desired obs. - if it hasn't run obs.
    if (not os.path.isfile(out_path + file_name \
         + '_geom_' + surf + 'Pow.csv')):
        print('\nComputing first return for observation: ' + file_name + '\n')
        main(rgramFile, surf = surf)
    else:
        print('\nSurface power extraction [' + surf + '] of observation' + rgramName \
            + ' already completed! Moving to next line!')

        
