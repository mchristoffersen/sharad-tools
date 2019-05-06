# Import necessary libraries
import numpy as np
import scipy
import matplotlib.pyplot as plt
import glob, os, sys, time
from read_Lbl import lbl_Parse
from read_Aux import aux_Parse
from read_Anc import anc_Parse
from read_Chirp import open_Chirp
from plotting import rgram
from read_EDR import EDR_Parse, sci_Decompress



def main(EDRName, auxName, lblName, chirp = 'calib', stackFac = None, beta = 0):
    """
    -----------
    This python function is used to pulse compress raw SHARAD EDRs to return chirp compressed science record. Output should be complex voltage.
    This code was adapted from Matthew Perry's @mr-perry FrankenRDR work, along with Michael Chrostoffersen's sharad-tools. Certain packages were directly updated from their work (ie. FrankenRDR-readLBL, readAnc, readAux). 
    This code simply aims to range compress the raw data.
    -----------
    Outputs:
    - raw-complex valued range compressed data
    - range compressed amplitude data
    - stacked range compressed amplitude data
    - nav data
    - stacked nav data
    - stacked radargram from range compressed amplitude data
    -----------
    Example call:  
    set desired parameters in __main__

    *if running through files in a directly:
        python range_Compress.py
    
    *elif using sys.argv[1] with list of file(s):
        python range_Compress.py 'files'
    -----------
    github: btobers
    Updated by: Brandon S. Tober
    Last Updated: 06MAY19
    -----------
    """
    t0 = time.time()                                            # start time
    print('--------------------------------')
    print(runName)
    print('--------------------------------')

    # extract relecant information from lbl file
    print('Reading label file...')
    lblDic = lbl_Parse(lblName)
    records = lblDic['FILE_RECORDS']                            # number of records in observation (traces)
    instrPresum = lblDic['INSTR_MODE_ID']['Presum']             # onboard presums
    instrMode = lblDic['INSTR_MODE_ID']['Mode']
    BitsPerSample = lblDic['INSTR_MODE_ID']['BitsPerSample']

    # toggle on to downsize for testing purposes
    # records = int(records / 100)

    # presumming is just for visualization purposes
    stackCols = int(np.floor(records/stackFac))

    # parse aux file into data frame
    auxDF = aux_Parse(auxName)

    # determine Bits per Sample
    if BitsPerSample == 4:
        recLen = 1986
    elif BitsPerSample == 6:
        recLen = 2886
    elif BitsPerSample == 8:
        recLen = 3786

    print('Instrument presum:\t' + format(instrPresum))
    print('Instrument mode:\t' + format(instrMode))
    print('Bits per sample:\t' + format(BitsPerSample))
    print('Record length:\t' + format(recLen))
    print('Number of records:\t' + format(records))
    print('Using Kaiser window of beta value:\t' + format(beta))
    print('---- Begin Processing ----')

    # determine TX and RX temps if using Italian reference chirp
    txTemp = auxDF['TX_TEMP'][:]
    rxTemp = auxDF['RX_TEMP'][:]	
    
    # read in reference chirps as matched filter - this should be imported in Fourier frequency domain, as complex conjugate
    if chirp == 'calib':
        refChirpMF, refChirpMF_index = open_Chirp(chirp, txTemp, rxTemp)
    else:
        refChirpMF = open_Chirp(chirp, txTemp, rxTemp)
    print('Reference chirp opened, type:\t' +  format(chirp))

    # read in raw science data and ancil data
    sci, ancil = EDR_Parse(EDRName, records, recLen, BitsPerSample)
    print('EDR science data parsed')

    # parse ancilliary data
    ancil = anc_Parse(ancil, records)
    print('Ancilliary data parsed')

    # create index to hold values of PRI in seconds
    pri = np.array([1428,1492,1290,2856,2984,2580])
    pri = pri * 1e-6
    
    # decompress science data
    sci = sci_Decompress(sci, lblDic['COMPRESSION'], instrPresum, BitsPerSample, ancil['SDI_BIT_FIELD'][:])
    print('EDR science data decompressed')

    # all data imported and decompressed
    # set up empty data arrays to hold Output and kaiser window of specified beta value
    if chirp =='ideal' or chirp == 'synth' or chirp == 'UPB':
        EDRData = np.zeros((3600,records), complex)
        ampStack = np.zeros((3600, stackCols))
        window = np.kaiser(3600, beta)

    elif chirp == 'calib':
        EDRData = np.zeros((4096,records), complex)
        ampStack = np.zeros((3600, stackCols))   
        window = np.pad(np.kaiser(2048,beta),(0,4096 - refChirpMF.shape[1]),'constant')        

    geomData = np.zeros((records,13))
    geomData_stack = np.zeros((stackCols,13))

    #-------------------
    # setup complete; begin range compression
    #------------------- 

    if chirp =='calib':
        refChirpMF_pad = np.pad(refChirpMF,[(0,0),(0,4096 - refChirpMF.shape[1])], 'constant')      # zeros pad reference chirp to length 4096 prior to range compression to account for missing sample in fourier spectra
        sciPad = np.pad(sci,[(0,4096 - sci.shape[0]),(0,0)],'constant')                             # zero-pad science data to length of 4096

        for _i in range(records):
            #-------------------
            # alternate method from PDS calinfo documentaion using reference chirp zero padded to 4096
            #-------------------
            sciFFT = np.fft.fft(sciPad[:,_i])
            dechirpData = (sciFFT * refChirpMF_pad[refChirpMF_index[_i],:]) * window
            EDRData[:,_i] = np.fft.ifft(dechirpData)

        # truncate revised and alternate range compressed vector to 3600
        EDRData = EDRData[:3600,:]

    else:
        for _i in range(records):
            #-------------------
            # range compression using ideal/ synthetic chirp
            #-------------------
            sciFFT = np.fft.fft(sci[:,_i])
            dechirpData = (sciFFT * refChirpMF) * window
            EDRData[:,_i] = np.fft.ifft(dechirpData)

    print('Range compression complete')

    # convert complex-valued voltage return to magnitude
    ampOut = np.abs(EDRData)

    # create geom array with relavant data for each record
    for _i in range(records):
        geomData[_i,0] = int(runName.split('_')[1] + runName.split('_')[2])
        geomData[_i,1] = int(_i)
        geomData[_i,2] = auxDF['X_MARS_SC_POSITION_VECTOR'][_i]
        geomData[_i,3] = auxDF['Y_MARS_SC_POSITION_VECTOR'][_i]
        geomData[_i,4] = auxDF['Z_MARS_SC_POSITION_VECTOR'][_i]
        geomData[_i,5] = auxDF['SPACECRAFT_ALTITUDE'][_i]
        geomData[_i,6] = auxDF['SUB_SC_EAST_LONGITUDE'][_i]
        geomData[_i,7] = auxDF['SUB_SC_PLANETOCENTRIC_LATITUDE'][_i]
        geomData[_i,8] = auxDF['SUB_SC_PLANETOGRAPHIC_LATITUDE'][_i]
        geomData[_i,9] = auxDF['MARS_SC_RADIAL_VELOCITY'][_i]
        geomData[_i,10] = auxDF['MARS_SC_TANGENTIAL_VELOCITY'][_i]
        geomData[_i,11] = auxDF['SOLAR_ZENITH_ANGLE'][_i]
        if (1/pri[(ancil['OST_LINE']['PULSE_REPETITION_INTERVAL'][_i]) - 1]) > 670.24 and (1/pri[(ancil['OST_LINE']['PULSE_REPETITION_INTERVAL'][_i]) - 1]) < 775.19:                               # time distance between start of transmission and the first sample of the received echo, as per http://pds-geosciences.wustl.edu/missions/mro/sharad.htm SHARAD EDR Data Product Software Interface Specification
            geomData[_i,12] = ((pri[(ancil['OST_LINE']['PULSE_REPETITION_INTERVAL'][_i]) - 1]) + (ancil['RECEIVE_WINDOW_OPENING_TIME'][_i] * 37.5e-9) - 11.98e-6)
        else:
            geomData[_i,12] = ((ancil['RECEIVE_WINDOW_OPENING_TIME'][_i] * 37.5e-9) - 11.98e-6)

    # stack data - amp radar data and geomdata - note: this cuts off remainder traces at the end if records not divisible by stackFac! 
    # also takes center trace from subset of stacked traces for geomData
    # currently set up for block stacking, may try and incorportate rolling average at some point
    if stackFac != 0
        for _i in range(stackCols):
            ampStack[:,_i] = np.mean(ampOut[:,stackFac*_i:stackFac*(_i+1)], axis = 1)
            geomData_stack[_i,0] = int(runName.split('_')[1] + runName.split('_')[2])
            geomData_stack[_i,1] = int(_i)
            geomData_stack[_i,2:] = geomData[int((stackFac*_i) + (((stackFac+1) / 2) - 1)),2:]
        np.savetxt(out_path + 'data/geom/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_geom_stack.csv', geomData_stack, delimiter = ',', newline = '\n', fmt ='%s')
        np.save(out_path + 'data/rgram/stack/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + chirp + '_' + windowName + '_slc_stack.npy', ampStack)
        print('Stacking complete')


    # create radargram and save data
    rgram(ampOut, out_path, runName, chirp, windowName, rel = True)
    np.savetxt(out_path + 'data/geom/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_geom.csv', geomData, delimiter = ',', newline = '\n', fmt ='%s')
    # np.save(out_path + 'data/rgram/comp/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + chirp + '_' + windowName + '_slc_raw.npy', EDRData)
    np.save(out_path + 'data/rgram/amp/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + chirp + '_' + windowName + '_slc_amp.npy', ampOut)
    print('Data output complete')
    

    t1 = time.time()        # end time
    print('--------------------------------')
    print('Total Runtime: ' + str(round((t1 - t0),4)) + ' seconds')
    print('--------------------------------')
    return

if __name__ == '__main__':
    # get correct data paths if depending on current OS
    # ---------------
    # INPUTS - set to desired parameters
    # ---------------
    study_area = 'bh_nh_bt/'  
    chirp = 'calib'
    beta = 0                # beta value for kaiser window [0 = rectangular, 5 	Similar to a Hamming, 6	Similar to a Hann, 8.6 	Similar to a Blackman]
    stackFac = 0            # stack factor - going with 5 to be safe and not incoherently stack - should be odd so center trace can be chosen for nav data                                     
    # ---------------
    mars_path = '/MARS'
    in_path = mars_path + '/orig/supl/SHARAD/EDR/' + study_area
    out_path = mars_path + '/targ/xtra/SHARAD/EDR/rangeCompress/' + study_area
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
    if (stackFac != 0) and ((stackFac % 2) == 0):
        print('If stacking, stackFac should be odd-numbered')
        sys.exit()
    if beta == 0:
        windowName = 'unif'
    elif beta == 5:
        windowName = 'hamming'
    elif beta == 6:
        windowName = 'hann'
    elif beta == 8.6:
        windowName = 'blackman'
    else:
        print('Unknown window type')
        sys.exit()

    # uncomment for testing single obs., enter lbl file as sys.argv[1] or for parellelizing range compression with list of .lbl files
    lbl_file = sys.argv[1]
    lblName = in_path + lbl_file
    runName = lbl_file.rstrip('_a.lbl')
    auxName = in_path + runName + '_a_a.dat'
    EDRName = in_path + runName + '_a_s.dat'
    main(EDRName, auxName, lblName, chirp = chirp, stackFac = stackFac, beta = beta)


    # uncomment for processing directory of obs.
    # for file in os.listdir(in_path):
    #     if file.endswith('.lbl'):
    #         lbl_file = file
    #         lblName = in_path + lbl_file
    #         runName = lbl_file.rstrip('_a.lbl')
    #         auxName = in_path + runName + '_a_a.dat'
    #         EDRName = in_path + runName + '_a_s.dat'

    # #         # if (not os.path.isfile(out_path + 'data/geom/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_geom.csv')):
    #         if (not os.path.isfile(out_path + 'browse/tiff/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + chirp + '_' + windowName + '_slc.tiff')):
    #             main(EDRName, auxName, lblName, chirp = chirp, stackFac = stackFac, beta = beta)
    #         else :
    #             print('\n' + runName + ' already processed!\n')
