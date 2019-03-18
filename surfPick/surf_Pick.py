# import necessary libraries
# from nadir import *
import os,sys
from PIL import Image
import math
import numpy as np
import scipy.misc
import time
# import matplotlib.pyplot as plt

def main(rgramFile, surfType = 'nadir'):
    '''
    script extracts power of surface return from radargram
    surface return can be defined as either first return (fret), nadir return, or 
    the max power return - return from which most radar energy penetrates surface (max)
    this will run through all .img radargrams in directory.
    designed to run on directory structured like PDS.

    author: Brandon S. Tober
    created: 30January2018
    updated: 27Feb019
    '''
    t0 = time.time()                                                                                                        # start time
    print('--------------------------------')
    print('Extracting surface power [' + surfType + '] for observation: ' + fileName)
    navFile = np.genfromtxt(in_path + 'processed/data/geom/' + fileName + '_geom.csv', delimiter = ',', dtype = None)       # open geom nav file for rgram to append surface echo power to each trace                                                 
    imarray = np.load(rgramFile)

    # imarray = imarray[:,::10]	                                                                                            # decrease the imarray to make testing faster
    # navFile = navFile[::10,:]
                                                                                         
    (r,c) = imarray.shape   
    C = np.empty((r,c))	                                                                                                    # create empty criteria array to localize surface echo for each trace
    pow = np.power(imarray,2)                                                                                               # convert amplitude radargram to power (squared amp)

    if surfType == 'nadir':

        ## Grab megt and mega from /disk/qnap-2/MARS/code/modl/MRO/simc/test/temp/dem/
        dem_path = mars_path + '/code/modl/MRO/simc/test/temp/dem/megt_128_merge.tif'

        binsize = .0375e-6

        speedlight = 3e8

        navdat = GetNav_geom(navPath)

        shift = navFile[:,12]
 
        topo = Dem(dem_path)

        nad_loc = navdat.toground(topo,navdat.csys)

        nadbin = np.zeros(len(navdat))
        nadbin2 = np.zeros(len(navdat))


        for i in range(len(navdat)):
            nadbin[i] = int(((navdat[i].z-nad_loc[i].z)*2/speedlight)/binsize) - shift[i]
            nadbin2[i] = int(((navdat[i].z-nad_loc[i].z)*2/speedlight)/binsize)

        # plt.subplot(2,2,1)
        # plt.title('PRI')
        # plt.plot(navFile[:,10])
        # plt.subplot(2,2,2)
        # plt.title('RECEIVE_WINDOW_OPEINING_TIME')
        # plt.plot(navFile[:,11])
        # plt.subplot(2,2,3)
        # plt.title('RECEIVE_WINDOW_POSITION_SHIFT')
        # plt.plot(shift)
        # plt.subplot(2,2,4)
        # plt.title('nadir_bin')
        # plt.plot(nadbin)
        # plt.suptitle('0589902_001')
        # plt.show()
        # sys.exit()

        surf = nadbin

    elif surfType == 'fret':
        '''       
        criteria for surface echo - indicator is Pt * dPt-1/dt, 
        where P is the signal energy applied on each grame sample (t).
        Indicator weights energy of a sample by the derivative preceding it
        '''

        gradient = np.gradient(pow, axis = 0)                                                                           # find gradient of each trace in RGRAM

        C[100:r,:] = pow[100:r,:]*gradient[99:r-1,:]                                                                    # vectorized criteria calculation
        
        C_max_ind = np.argmax(C, axis = 0)	                                                                                # find indices of max critera seletor for each column

        surf = C_max_ind
    
    elif surfType == 'max':
        print('Code not set up to handle max power return as of yet - BT')
        sys.exit()
        
    # rescale rgram for visualization to plot surfPick
    maxPow = np.argmax(pow, axis = 0)                                                                                   # find max power (or amplitude) in each trace to compare with fret algorithm
    noise_floor = np.mean(pow[:50,:])                                                                                       # define a noise floor from average power of flattened first 50 rows
    dB = 10 * np.log10(pow / noise_floor)                                                                                   # scale image array by max pixel to create jpg output with fret index
    maxdB = np.amax(dB, axis = 0)
    imarrayScale = dB / maxdB * 255
    imarrayScale[np.where(imarrayScale < 0)] = 0.
    imarrayScale[np.where(imarrayScale > 255)] = 255.
    imarrayScale = np.abs(imarrayScale - 255)

    surfIndex = np.zeros((r,c,3), 'uint8')	                                                                                # create empty surf index and power arrays
    surfPow = np.empty((c,1))

    surfIndex[:,:,0] = surfIndex[:,:,1] = surfIndex[:,:,2] = imarrayScale[:,:]                                              # create surf index image - show scaled radargram as base
    
    surfIndex[maxPow, np.arange(c),0:2] = 0                                                                                 # indicate max power along track as red
    surfIndex[maxPow, np.arange(c),0] = 255  

    surfIndex[surf, np.arange(c),0] = surfIndex[surf, np.arange(c),1] = 255                                                 # make index given by fret algorithm yellow
    surfIndex[surf, np.arange(c),2] = 0
    
    surfAmp = np.reshape(imarray[surf, np.arange(c)], (c,1))                                                                # record power in dB
    surfPow = 20 * (np.reshape((np.log10(surfAmp)),(c,1)))

    if navFile.shape[1] == 13:                                                                                              # append surf pow values to geom.tab file. this should be the 11th column
        navFile = np.append(navFile, surfAmp, 1)

    else:                                                                                                                   # if surfPow with specified surf has already been run and it is being re-run, overwrite 6th column with new pow values
        navFile[:,14] = surfAmp[:,0]

    np.savetxt(out_path + fileName + '_geom_' + surfType + '.csv', navFile, delimiter = ',', newline = '\n', fmt= '%s')
    np.savetxt(out_path + fileName + '_' + surfType + '_pow.txt', surfAmp, delimiter=',', newline = '\n', comments = '', header = 'PDB', fmt='%.8f')

    try:
        surfArray = Image.fromarray(surfIndex[:,::32], 'RGB')                                                               # downsample by taking every 32nd trace for output fret image
        scipy.misc.imsave(out_path + fileName + '_' + surfType + '.png', surfArray)
    except Exception as err:
        print(err)

    t1 = time.time()                                                                                                        # end time
    print('Total Runtime: ' + str(round((t1 - t0),4)) + ' seconds')
    print('--------------------------------')
    return

if __name__ == '__main__':
    
    # get correct data paths if depending on current OS
    mars_path = '/MARS'
    in_path = mars_path + '/orig/supl/SHARAD/EDR/bh_nh_bt/'
    out_path = mars_path + '/targ/xtra/SHARAD/surfPow/bh_nh_bt/'
    if os.getcwd().split('/')[1] == 'media':
        mars_path = '/media/anomalocaris/Swaps' + mars_path
        in_path = '/media/anomalocaris/Swaps' + in_path
        out_path = '/media/anomalocaris/Swaps' + out_path
    elif os.getcwd().split('/')[1] == 'mnt':
        mars_path = '/mnt/d' + mars_path
        in_path = '/mnt/d' + in_path
        out_path = '/mnt/d' + out_path
    elif os.getcwd().split('/')[1] == 'disk':
        mars_path = '/disk/qnap-2' + mars_path
        in_path = '/disk/qnap-2' + in_path
        out_path = '/disk/qnap-2' + out_path
    else:
        print('Data path not found')
        sys.exit()
   
    rgramFile = sys.argv[1]                                                                                                 # input radargram - range compressed - amplitude output
    fileName = rgramFile.split('_')[0] + '_' + rgramFile.split('_')[1]                                                      # base fileName
    rgramName = fileName.split('_')[0] + fileName.split('_')[1]                                                             # SHARAD rgram obs. #
    navPath = in_path + 'processed/data/geom/' + fileName + '_geom.csv'                                                     # path to nav file for obs.  
    rgramFile = in_path + 'processed/data/rgram/amp/' + rgramFile                                                           # attach input data path to beginning of rgram file name
    surfType = 'fret'                                                                                                           # define the desired surface pick = [fret,narid,max]

    
    # check if surfPow has already been determined for desired obs. - if it hasn't run obs.
    if (not os.path.isfile(out_path + fileName \
         + '_geom_' + surfType + 'Pow.csv')):
        main(rgramFile, surfType = surfType)
    else:
        print('\nSurface power extraction [' + surfType + '] of observation' + rgramName \
            + ' already completed! Moving to next line!')

        
