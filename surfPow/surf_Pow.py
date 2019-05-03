# import necessary libraries
from nadir import *
import os,sys
from PIL import Image
import math
import numpy as np
import scipy.misc
import time
import matplotlib.pyplot as plt

def main(rgramPath, surfType = 'nadir'):
    '''
    function extracts power of surface return from radargram
    surface return can be defined as either first return (fret), nadir return, or 
    the max power return - return from which most radar energy penetrates surface (max)
    this will run through all .img radargrams in directory.
    designed to run on directory structured like PDS.

    author: Brandon S. Tober
    created: 30January2018
    updated: 24APR19
    '''
    t0 = time.time()                                                                                                        # start time
    fileName = rgramPath.split('/')[-1]
    fileName = fileName.split('_')[0] + '_' + fileName.split('_')[1]

    print('--------------------------------')
    print('Extracting surface power [' + surfType + '] for observation: ' + fileName)
    
    if dataSet == 'amp':
        navPath = in_path + 'data/geom/' + fileName + '_geom.csv'
    elif dataSet =='stack':
        navPath = in_path + 'data/geom/' + fileName + '_geom_stack.csv'

    navFile = np.genfromtxt(navPath, delimiter = ',', dtype = None)                                                         # open geom nav file for rgram to append surface echo power to each trace                                                 
    amp = np.load(rgramPath)
    pow = np.power(amp,2)                                                                                                   # convert amplitude radargram to power (squared amp)                                          
    (r,c) = amp.shape   
    nadbin = np.zeros(c)                                                                                                # empty array to hold pixel location for each trace of nadir location
    binsize = .0375e-6
    speedlight = 3e8#299792458
    shift = navFile[:,12]                                                                                               # receive window opening time shift from EDR aux data

    dem_path = mars_path + '/code/modl/MRO/simc/test/temp/dem/megt_128_merge.tif'                                       # Grab megt and mega,  mola dem and aeroid 
    aer_path = mars_path + '/code/modl/MRO/simc/test/temp/dem/mega_16.tif'

    navdat = GetNav_geom(navPath)

    topo = Dem(dem_path)

    nad_loc = navdat.toground(topo,navdat.csys)

    aer = Dem(aer_path)

    aer_nadir = navdat.toground(aer)

    for i in range(len(navdat)):
        if(aer_nadir[i].z == aer.nd):
            aer_nadir[i].z = aer_nadir[i-1].z
        navdat[i].z = navdat[i].z - aer_nadir[i].z                                                                      # MRO elevation above aeroid: subtract out spheroid and aeroid
        if np.abs(nad_loc[i].z) > 1e10:                                                                                 # account for no data values from mola dem - assign previous value if n.d.
            nad_loc[i].z = nad_loc[i-1].z
        nadbin[i] = int(((((navdat[i].z-nad_loc[i].z) * 2 / speedlight) - shift[i]) / binsize) + 55)                    # take MRO height above aeroid, subtract mola elevation, account for SHARAD receive window opening time shift and convert to pixels 
        nadbin[i] = nadbin[i] % 3600                                                                                    # take modulo in case pixel is location of nadir is greater then max rgram dimensions
    nadbin = nadbin.astype(int)
    if surfType == 'nadir':
        surf = nadbin

    elif surfType == 'fret':
        '''       
        criteria for surface echo - indicator is Pt * dPt-1/dt, 
        where P is the signal energy applied on each grame sample (t).
        Indicator weights energy of a sample by the derivative preceding it
        '''
        C = np.empty((r,c))	                                                                                                # create empty criteria array to localize surface echo for each trace
        
        C_wind = np.zeros((2*window,c))
        
        gradient = np.gradient(pow, axis = 0)                                                                               # find gradient of each trace in RGRAM

        C[100:r,:] = pow[100:r,:]*gradient[99:r-1,:]                                                                        # vectorized criteria calculation


        for _i in range(c):
            C_wind[:,_i] = C[nadbin[_i] - window : nadbin[_i] + window,_i]
        
        C_max_window_ind = np.argmax(C_wind, axis = 0)                                                                      # find indices of max critera seletor for each column

        surf = C_max_window_ind

        surf[:] = surf[:] + nadbin[:] - window
    
    elif surfType == 'max':
        print('Code not set up to handle max power return as of yet - BT')
        sys.exit()


    # record surface power in text file and geomdata file
    surf = surf.astype(int)
    surfAmp = np.reshape(amp[surf, np.arange(c)], (c,1))                                                                    # record power in dB
    surfPow = 20 * (np.log10(surfAmp))


    if navFile.shape[1] == 13:                                                                                              # append surf pow values to geom.tab file. this should be the 13th column
        navFile = np.append(navFile, surfAmp, 1)

    else:                                                                                                                   # if surfPow with specified surf has already been run and it is being re-run, overwrite 6th column with new pow values
        navFile[:,14] = surfAmp[:,0]

    if dataSet == 'amp':
        np.savetxt(out_path + fileName + '_geom_' + surfType + '.csv', navFile, delimiter = ',', newline = '\n', fmt= '%s')
        np.savetxt(out_path + fileName + '_' + surfType + '_pow.txt', surfAmp, delimiter=',', \
        newline = '\n', comments = '', fmt='%.8f')
    elif dataSet == 'stack':
        np.savetxt(out_path + fileName + '_geom_' + dataSet + '_' + surfType + '.csv', navFile, delimiter = ',', newline = '\n', fmt= '%s')
        np.savetxt(out_path + fileName + '_' + dataSet + '_' + surfType + '_pow.txt', surfAmp, delimiter=',', \
        newline = '\n', comments = '', fmt='%.8f')

    maxPow = np.argmax(pow, axis = 0)                                                                                       # find max power in each trace
    noise_floor = np.mean(pow[:50,:])                                                                                       # define a noise floor from average power of flattened first 50 rows
    dB = 10 * np.log10(pow / noise_floor)                                                                                   # scale image array by max pixel to create jpg output with fret index
    maxdB = np.amax(dB, axis = 0)
    ampScale = dB / maxdB * 255
    ampScale[np.where(ampScale < 0)] = 0.
    ampScale[np.where(ampScale > 255)] = 255.
    # ampScale = np.abs(ampScale - 255)                                                                                       # reverse color scheme black on white

    # print(np.median(np.abs(surf - maxPow)))
    # plt.plot(np.abs(surf - maxPow))
    # plt.show()

    imarray = np.zeros((r,c,3), 'uint8')                                                                                    # create empty surf index and power arrays
    imarray[:,:,0] = imarray[:,:,1] = imarray[:,:,2] = ampScale[:,:]                                                        # create surf index image - show scaled radargram as base

    imarray[maxPow, np.arange(c),0:2] = 0                                                                                   # indicate max power along track as red
    imarray[maxPow, np.arange(c),0] = 255  

    imarray[nadbin, np.arange(c),0] = 0                                                                                     # indicate nadir position as cyan
    imarray[nadbin, np.arange(c),1] = imarray[nadbin, np.arange(c),2] = 255

    imarray[surf, np.arange(c),0] = imarray[surf, np.arange(c),1] = 255                                                     # make index given by fret algorithm yellow
    imarray[surf, np.arange(c),2] = 0

    try:
        if dataSet == 'amp':
            im = Image.fromarray(imarray[:,::32], 'RGB')            
            scipy.misc.imsave(out_path + fileName + '_' + surfType + '.png', im)
        elif dataSet == 'stack':                                   
            im = Image.fromarray(imarray[:,::5], 'RGB')
            scipy.misc.imsave(out_path + fileName + '_' + dataSet + '_' + surfType + '.png', im)
    except Exception as err:
        print(err)

    t1 = time.time()                                                                                                        # end time
    print('Total Runtime: ' + str(round((t1 - t0),4)) + ' seconds')
    print('--------------------------------')
    return

if __name__ == '__main__':
    
    # get correct data paths if depending on current OS
    # ---------------
    # set to desired parameters
    # ---------------
    study_area = 'hebrus_valles_sn/'
    surfType = 'fret'                                                                                                       # define the desired surface pick = [fret,narid,max]
    window = 100                                                                                                            # define window for computing fret algorithm around window of nadir location
    dataSet = 'stack'                                                                                                       # data set to use (amp or stack)
    # ---------------
    mars_path = '/MARS'
    in_path = mars_path + '/targ/xtra/SHARAD/EDR/rangeCompress/' + study_area
    out_path = mars_path + '/targ/xtra/SHARAD/EDR/surfPow/' + study_area
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
   
    # ---------------
    # set up for running on single obs, or list of obs with parallels using sys.argv[1]
    # ---------------
    rgramPath = sys.argv[1]                                                                                                 # input radargram - range compressed - amplitude output
    fileName = rgramPath.split('_')[0] + '_' + rgramPath.split('_')[1]                                                      # base fileName
    rgramPath = in_path + 'data/rgram/' + dataSet + '/' + rgramPath                                                           # attach input data path to beginning of rgram file name
  
    # check if surfPow has already been determined for desired obs. - if it hasn't run obs.
    if (not os.path.isfile(out_path + fileName \
         + '_geom_' + surfType + 'Pow.csv')):
        main(rgramPath, surfType = surfType)
    else:
        print('\nSurface power extraction [' + surfType + '] of observation' + fileName \
            + ' already completed!')
    
    # ---------------
    # set up for running on directory on obs at a time - this currently does not work - navdat gets appended to for nadir surface with each obs.
    # ---------------
    # for file in os.listdir(in_path + 'data/rgram/amp/'):
    #     if file.endswith('slc_amp.npy'):
    #         rgramPath = file
    #         rgramPath = in_path + 'data/rgram/amp/' + rgramPath
    #         fileName = rgramPath.split('/')[-1]
    #         fileName = fileName.split('_')[0] + '_' + fileName.split('_')[1]

    #         if (not os.path.isfile(out_path + fileName + '_' + surfType + '.png')):
    #             main(rgramPath, surfType = surfType)
    #         else :
    #             print('\nSurface power extraction [' + surfType + '] of observation ' + fileName \
    #         + ' already completed! Moving to next line!')

        
