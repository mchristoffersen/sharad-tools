# import necessary libraries
import nadir
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
    updated: 27Feb019
    '''
    t0 = time.time()                                                                                                        # start time
    print('--------------------------------')
    print(rgramName)
    print('--------------------------------')

    imarray = np.load(rgramFile)

    # imarray = imarray[:,0:100:1]	                                                                                        # decrease the imarray to make testing faster
    # navFile = navFile[0:100:1,:]	                                                                                       

    (r,c) = imarray.shape   
    C = np.empty((r,c))	                                                                                                    # create empty criteria array to localize surface echo for each trace

    if surf == 'nadir':

        ## Grab megt and mega from /disk/qnap-2/MARS/code/modl/MRO/simc/test/temp/dem/

        dem_path = "path/to/dem"

        binsize = .0375e-6

        speedlight = 3e8

        navdat = GetNav_geom(navPath)

        recwindow = navFile[:,9]

        shift = [0]*len(navdat)
        for i in range(len(navdat)):
            shift[i] = int((recwindow[i])/binsize)       

        topo = Dem(dem_path)

        nad_loc = navdat.toground(topo,navsys)

        nadbin = [0]*len(navdat)

        for i in range(len(navdat)):
            nadbin[i] = int(((navdat[i].z-nad_loc[i].z)*2/speedlight)/binsize) - shift[i]

        surf = nadbin

    elif surf == 'fret':
        '''       
        criteria for surface echo - indicator is Pt * dPt-1/dt, 
        where P is the signal energy applied on each grame sample (t).
        Indicator weights energy of a sample by the derivative preceding it
        '''

        gradient = np.gradient(imarray, axis = 0)                                                                           # find gradient of each trace in RGRAM

        C[100:r,:] = imarray[100:r,:]*gradient[99:r-1,:]                                                                    # vectorized criteria calculation
        
        C_max_ind = np.argmax(C, axis = 0)	                                                                                # find indices of max critera seletor for each column

        surf = C_max_ind
    
    elif surf == 'max':
        print('Code not set up to handle max power return as of yet - BT')
        sys.exit()


    # rescale rgram for visualization to plot surfPick
    maxAmp = np.argmax(imarray, axis = 0)                                                                                   # find max power (or amplitude) in each trace to compare with fret algorithm
    dB = 10 * np.log10(imarray / np.mean(pow[:50,:]))                                                                       # scale image array by max pixel to create jpg output with fret index
    imarrayScale = ((dB / np.amax(dB)) * 255)
    imarrayScale[ np.where(imarrayScale > 50) ] = 255


    surfIndex = np.zeros((r,c,3), 'uint8')	                                                                                # create empty surf index and power arrays
    surfPow = np.empty((c,1))


    surfIndex[:,:,0] = surfIndex[:,:,1] = surfIndex[:,:,2] = imarrayScale[:,:]                                              # create surf index image - show scaled radargram as base
    
    surfIndex[maxAmp, np.arange(c),0:2] = 0                                                                                 # indicate max power along track as red
    surfIndex[maxAmp, np.arange(c),0] = 255  

    surfIndex[surf, np.arange(c),0] = surfIndex[surf, np.arange(c),1] = 255                                                 # make index given by fret algorithm yellow
    surfIndex[surf, np.arange(c),2] = 0
    
    surfAmp = imarray[surf, np.arange(c)]                                                                                   # record power in dB
    surfPow = 20 * (np.reshape((np.log10(surfAmp)),(c,1)))

    if navFile.shape[1] == 10:                                                                                              # append surf pow values to geom.tab file. this should be the 11th column
        navFile = np.append(navFile, surfPow, 1)

    else:                                                                                                                   # if surfPow with specified surf has already been run and it is being re-run, overwrite 6th column with new pow values
        navFile[:,11] = surfPow[:,0]
        
    np.savetxt(out_path + 'geom/' + fileName + '_geom2.csv', navFile, delimiter = ',', newline = '\n', fmt= '%s')
    np.savetxt(out_path + '/fret/' + fileName + '_surf_pow.txt', surfPow, delimiter=',', newline = '\n', comments = '', header = 'PDB', fmt='%.8f')

    try:
        surfArray = Image.fromarray(surfIndex[:,::32], 'RGB')                                                               # downsample by taking every 32nd trace for output fret image
        scipy.misc.imsave(data_path + 'out/fret/' + fileName + '_' + surf + '.jpg', surfArray)
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
    navPath = in_path + 'data/geom/' + fileName + '_geom.csv'                                                               # path to nav file for obs.  
    navFile = np.genfromtxt(in_path + 'data/geom/' + fileName + '_geom.csv', delimiter = ',', dtype = str)                  # open geom nav file for rgram to append surface echo power to each trace                                                 
    surf = 'nadir'                                                                                                          # define the desired surface pick = [fret,narid,max]

    
    # check if surfPow has already been determined for desired obs. - if it hasn't run obs.
    if (not os.path.isfile(out_path + fileName \
         + '_geom_' + surf + 'Pow.csv')):
        print('\nExtracting surface power for observation: ' + fileName + '\n')
        main(rgramFile, surf = surf)
    else:
        print('\nSurface power extraction [' + surf + '] of observation' + rgramName \
            + ' already completed! Moving to next line!')

        
