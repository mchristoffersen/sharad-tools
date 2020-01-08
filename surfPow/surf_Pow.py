# import necessary libraries
from nadir import *
import os,sys
from PIL import Image
import numpy as np
import time

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def main(rgramPath, surfType = 'nadir'):
    '''
    function extracts power of surface return from radargram
    surface return can be defined as either first return (fret), nadir return, or 
    the max power return - return from which most radar energy penetrates surface (max)
    this will run through all .img radargrams in directory.
    designed to run on directory structured like PDS.

    example call:

    python surf_Pow.py [verbose] [study_area] [surface type] [window size] [range compressed amplitude data file]

    argv[1] is the verbose setting
    argv[2] is study area within $MARS/targ/xtra/SHARAD/EDR/rangeCompress/
    argv[3] is the desired surface type to extract the reflectivity of 
    argv[4] is the desired window size (# of samples), centered on the nadir surface
    argv[5] is single obs. file or list of obs. files within  $MARS/targ/xtra/SHARAD/EDR/rangeCompress/[study_area]/data/rgram/amp/

    author: Brandon S. Tober
    created: 30January2018
    updated: 03January2020
    '''
    t0 = time.time()                                                                                                        # start time
    fileName = rgramPath.split('/')[-1]
    fileName = fileName.split('_')[0] + '_' + fileName.split('_')[1]

    print('--------------------------------')
    print('Extracting surface power [' + surfType + '] for observation: ' + fileName)
    

    dem_path = '/zippy/MARS/code/modl/simc/test/temp/dem/megt_128_merge.tif'                                       # Grab megt and $
    aer_path = '/zippy/MARS/code/modl/simc/test/temp/dem/mega_16.tif'


    if dataSet == 'amp':
        navPath = in_path + 'data/geom/' + fileName + '_geom.csv'
    elif dataSet =='stack':
        navPath = in_path + 'data/geom/' + fileName + '_geom_stack.csv'

    navFile = np.genfromtxt(navPath, delimiter = ',', dtype = None, names = True)                                                         # open geom nav file for rgram to append surface echo power to each trace                                                 
    amp = np.load(rgramPath)
    pow = np.power(amp,2)                                                                                                   # convert amplitude radargram to power (squared amp)                                          
    (r,c) = amp.shape   
    nadbin = np.zeros(c)                                                                                                # empty array to hold pixel location for each trace of nadir location
    binsize = .0375e-6
    speedlight = 299792458
    shift = navFile['RECEIVE_WINDOW_OPENING_TIME']                                                                                               # receive window opening time shift from EDR aux data

    navdat = GetNav_geom(navPath)                                                                                       # convert x,y,z MRO position vectors to spheroid referenced lat,long, radius

    topo = Dem(dem_path)                                                                                                # create DEM class from aeroid
    nad_loc = navdat.toground(topo,navdat.csys)                                                                         # convert nav DEM to ground points, x,y,z - spheroid referenced

    aer = Dem(aer_path)                                                                                                 # create DEM class from aeroid
    aer_nadir = navdat.toground(aer,navdat.csys)                                                                        # convert aeroid DEM to ground points, x,y,z - spheroid referenced

    for i in range(len(navdat)):
        if(aer_nadir[i].z == aer.nd):
            aer_nadir[i].z = aer_nadir[i-1].z                                                                           # account for aeroid no data values
        navdat[i].z = navdat[i].z - aer_nadir[i].z                                                                      # MRO elevation above aeroid: subtract out aeroid
        
        if np.abs(nad_loc[i].z) > 1e10:                                                                                 # account for no data values from mola dem - assign previous value if n.d.
            nad_loc[i].z = nad_loc[i-1].z
 
        nadbin[i] = ((((navdat[i].z-nad_loc[i].z) * 2 / speedlight) - shift[i]) / binsize) + 55                         # take MRO height above aeroid, subtract mola elevation, account for SHARAD receive window opening time shift and convert to pixels ### 55 pixels added to place nadir surface at relatively correct place - need to add ionosphereic correction
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
        C_wind = np.zeros((window,c))

        gradient = np.gradient(pow, axis = 0)                                                                               # find gradient of each trace in RGRAM
        C[100:r,:] = pow[100:r,:]*gradient[99:r-1,:]                                                                        # vectorized criteria calculation

        good = []                                                                                                           # intialize list of traces where windowing did work 
        bad = []                                                                                                            # intialize list of traces where windowing did not work    
                
        try:
            for _i in range(c):
                if (nadbin[_i] - int(window / 2) > 0) and (nadbin[_i] + int(window / 2) < r):
                    C_wind[:,_i] = C[nadbin[_i] - int(window / 2) : nadbin[_i] + int(window / 2),_i]
                    good.append(str(_i))

                else:
                    bad.append(str(_i))                                                                                     # keep track of traces where windowing did not work
            
            good = np.asarray(good).astype(int)
            bad = np.asarray(bad).astype(int)
            
            C_max_window_ind = np.argmax(C_wind, axis = 0)                                                                  # find indices of max critera seletor for each column            
            C_max_window_ind[bad[:]] = np.argmax(C[:,bad[:]], axis = 0)                                                     # where windowing does not work, provide max fret pixel from entire trace
            
            surf = C_max_window_ind
            surf[good[:]] = surf[good[:]] + nadbin[good[:]] - (window / 2)                                                  # where windowing does work, add pixel indices to get proper location

        except Exception as err:
            print(err)
            print('Calculating first return without windowing')
            surf = np.argmax(C, axis =0)



    
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

    maxPow = np.argmax(pow, axis = 0)                                                                                       # find max power in each trace
    noise_floor = np.mean(pow[:50,:])                                                                                       # define a noise floor from average power of flattened first 50 rows
    dB = 10 * np.log10(pow / noise_floor)                                                                                   # scale image array by max pixel to create jpg output with fret index
    maxdB = np.amax(dB, axis = 0)
    ampScale = dB / maxdB * 255
    ampScale[np.where(ampScale < 0)] = 0.
    ampScale[np.where(ampScale > 255)] = 255.
    # ampScale = np.abs(ampScale - 255)                                                                                       # reverse color scheme black on white

    imarray = np.zeros((r,c,3), 'uint8')                                                                                    # create empty surf index and power arrays
    imarray[:,:,0] = imarray[:,:,1] = imarray[:,:,2] = ampScale[:,:]                                                        # create surf index image - show scaled radargram as base

    imarray[maxPow, np.arange(c),0:2] = 0                                                                                   # indicate max power along track as red
    imarray[maxPow, np.arange(c),0] = 255  

    imarray[nadbin, np.arange(c),0] = 0                                                                                     # indicate nadir position as cyan
    imarray[nadbin, np.arange(c),1] = imarray[nadbin, np.arange(c),2] = 255

    imarray[surf, np.arange(c),0] = imarray[surf, np.arange(c),1] = 255                                                     # make index given by fret algorithm yellow
    imarray[surf, np.arange(c),2] = 0

    if dataSet == 'amp':
        np.savetxt(out_path + fileName + '_' + surfType + '_geom.csv', navFile, delimiter = ',', newline = '\n', fmt= '%s')
        np.savetxt(out_path + fileName + '_' + surfType + '_pow.txt', surfAmp, delimiter=',', newline = '\n', comments = '', fmt='%.8f')
        try:
            Image.fromarray(imarray[:,::32], 'RGB').save(out_path + fileName + '_' + dataSet + '_' + surfType + '.jpg')
        except Exception as err:
            print(err)
            
    elif dataSet == 'stack':
        np.savetxt(out_path + fileName + '_' + dataSet + '_' + surfType + '_geom.csv', navFile, delimiter = ',', newline = '\n', fmt= '%s')
        np.savetxt(out_path + fileName + '_' + dataSet + '_' + surfType + '_pow.txt', surfAmp, delimiter=',', newline = '\n', comments = '', fmt='%.8f')
        try:
            Image.fromarray(imarray, 'RGB').save(out_path + fileName + '_' + dataSet + '_' + surfType + '.jpg')
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
    verbose = int(sys.argv[1])
    if verbose == 0:
        blockPrint()
    study_area = sys.argv[2] + '/' 
    surfType = sys.argv[3]                                                                                        # define the desired surface pick = [fret,narid,max]
    window = int(sys.argv[4])                                                                                             # define window for computing fret algorithm around window of nadir location - larger window may be used as nadir location does not currently line up well for all obs. larger window may account for this.
    # ---------------
    in_path = '/zippy/MARS/targ/xtra/SHARAD/EDR/rangeCompress/' + study_area
    out_path = '/zippy/MARS/targ/xtra/SHARAD/EDR/surfPow/' + study_area
    # if os.getcwd().split('/')[1] == 'media':
    #     mars_path = '/media/anomalocaris/Swaps' + mars_path
    #     in_path = '/media/anomalocaris/Swaps' + in_path
    #     out_path = '/media/anomalocaris/Swaps' + out_path
    # elif os.getcwd().split('/')[1] == 'mnt':
    #     mars_path = '/mnt/d' + mars_path
    #     in_path = '/mnt/d' + in_path
    #     out_path = '/mnt/d' + out_path
    # elif os.getcwd().split('/')[1] == 'zippy':
    #     mars_path = '/disk/qnap-2' + mars_path
    #     in_path = '/disk/qnap-2' + in_path
    #     out_path = '/disk/qnap-2' + out_path
    # elif os.getcwd().split('/')[1] == 'home':
    #     mars_path = '/home/btober/Documents' + mars_path
    #     in_path = '/home/btober/Documents' + in_path
    #     out_path = '/home/btober/Documents' + out_path
    # else:
    #     print('Data path not found')
    #     sys.exit()

    # create necessary output directories
    try:
        os.makedirs(out_path)
    except FileExistsError:
        pass
   
    # ---------------
    # set up for running on single obs, or list of obs with parallels using sys.argv[1]
    # ---------------
    rgramPath = sys.argv[5]                                                                                                 # input radargram - range compressed - amplitude output
    fileName = rgramPath.split('_')[0] + '_' + rgramPath.split('_')[1]                                                      # base fileName
    dataSet = (rgramPath.split('_')[-1]).split('.')[0]                                                                      # data set to use (amp or stack)
    rgramPath = in_path + 'data/rgram/' + dataSet + '/' + rgramPath                                                         # attach input data path to beginning of rgram file name
  
    # check if surfPow has already been determined for desired obs. - if it hasn't run obs.
    if dataSet == 'amp':
        if (not os.path.isfile(out_path + fileName + '_' + surfType + '_geom.csv')):
            main(rgramPath, surfType = surfType)
        else:
            print('Surface power extraction [' + surfType + '] of observation ' + fileName + ' already completed!')
    elif dataSet == 'stack':
        if (not os.path.isfile(out_path + fileName + '_' + dataSet + '_' + surfType + '_geom.csv')):
            main(rgramPath, surfType = surfType)
        else:
            print('Surface power extraction [' + surfType + '] of observation ' + fileName + ' already completed!')
    
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