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
    This python script is used to pulse compress raw SHARAD EDRs to return chirp compressed science record. Output should be complex voltage.
    This code was adapted from Matthew Perry's @mr-perry FrankenRDR work, along with Michael Chrostoffersen's sharad-tools. Certain packages were directly updated from their work (ie. FrankenRDR-readLBL, readAnc, readAux). 
    This code simply aims to pulse compress the raw data, without performing any other processing steps.

    github: b-tober
    Updated by: Brandon S. Tober
    Last Updated: 10Jan2019
    -----------
    Example call:

    EDRName = '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a_s.dat'
    auxName =  '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a_a.dat'
    lblName =  '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a.lbl'
    chirp = 'calib'
    stackFac = 8
    beta = 0

    main(EDRName, auxName, lblName, chirp = chirp, stackFac = stackFac)
    """
    t0 = time.time()                                            #start time
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
    records = int(records / 100)


    # presumming is just for visualization purposes
    presumCols = int(np.ceil(records/stackFac))

    # parse aux file into data frame
    auxDF = aux_Parse(auxName)

    # determine Bits per Sample
    if BitsPerSample == 4:
        recLen = 1986
    elif BitsPerSample == 6:
        recLen = 2886
    elif BitsPerSample == 8:
        recLen = 3786

    print('InstrPresum:\t' + format(instrPresum))
    print('Instrument Mode:\t' + format(instrMode))
    print('Bits Per Sample:\t' + format(BitsPerSample))
    print('Record Length:\t' + format(recLen))
    print('Number of Records:\t' + format(records))
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
    print('EDR Science Data Parsed')

    # parse ancilliary data
    ancil = anc_Parse(ancil, records)
    print('Ancilliary Data Parsed')

    # decompress science data
    sci = sci_Decompress(sci, lblDic['COMPRESSION'], instrPresum, BitsPerSample, ancil['SDI_BIT_FIELD'][:])
    print('EDR Science Data Decompressed')

    # all data imported and decompressed
    # set up empty data arrays to hold Output and kaiser window of specified beta value
    if chirp =='ideal' or chirp == 'synth' or chirp == 'UPB':
        EDRData = np.zeros((3600,records), complex)
        ampStack = np.zeros((3600, presumCols))
        window = np.kaiser(3600, beta)

    elif chirp == 'calib':
        EDRData = np.zeros((4096,records), complex)
        ampStack = np.zeros((3600, presumCols))   
        window = np.pad(np.kaiser(2048,beta),(0,4096 - refChirpMF.shape[1]),'constant')        

    geomData = np.zeros((records,5))

    #-------------------
    # setup complete; begin range compression
    #------------------- 

    if chirp =='calib':
        refChirpMF_pad = np.pad(refChirpMF,[(0,0),(0,4096 - refChirpMF.shape[1])], 'constant')      # zeros pad reference chirp to length 2049 prior to range compression to account for missing sample in fourier spectra
        sciPad = np.pad(sci,[(0,4096 - sci.shape[0]),(0,0)],'constant')                             # zero-pad science data to length of 4096

        for _i in range(records):
            #-------------------
            # alternate method from PDS calinfo documentaion using reference chirp zero padded to 4096
            #-------------------
            sciFFT = np.fft.fft(sciPad[:,_i])
            dechirpData = (sciFFT * refChirpMF_pad[refChirpMF_index[_i],:]) * window
            EDRData[:,_i] = np.fft.ifft(dechirpData)

        #truncate revised and alternate range compressed vector to 3600
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

    # stack data
    for _i in range(presumCols - 1):
        ampStack[:,_i] = np.mean(ampOut[:,stackFac*_i:stackFac*(_i+1)], axis = 1)

    # account for traces left if number of traces is not divisible by stackFac
    ampStack[:,-1] = np.mean(ampOut[:,stackFac*(_i+1):-1], axis = 1)
    print('Stacking complete')

    # create geom array with relavant data for each record
    for _i in range(records):
        geomData[_i,0] = runName.split('_')[1] + runName.split('_')[2]
        geomData[_i,1] = int(_i)
        geomData[_i,2] = auxDF['SUB_SC_PLANETOCENTRIC_LATITUDE'][_i]
        geomData[_i,3] = auxDF['SUB_SC_EAST_LONGITUDE'][_i]
        geomData[_i,4] = auxDF['SOLAR_ZENITH_ANGLE'][_i]

    # create radargrams from presummed data to ../../orig/supl/SHARAD/EDR/EDR_pc_brucevisualize output, also save data
    rgram(ampStack, data_path, runName, chirp, windowName, rel = True)
    np.savetxt(data_path + 'processed/data/geom/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_geom.csv', geomData, delimiter = ',', newline = '\n',fmt = '%s')
    np.save(data_path + 'processed/data/rgram/comp/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + chirp + '_' + windowName + '_slc_raw.npy', EDRData)
    np.save(data_path + 'processed/data/rgram/amp/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + chirp + '_' + windowName + '_slc_amp.npy', ampOut)
    np.save(data_path + 'processed/data/rgram/stack/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + chirp + '_' + windowName + '_slc_stack.npy', ampStack)

    t1 = time.time()    # End time
    print('--------------------------------')
    print('Total Runtime: ' + str(round((t1 - t0),4)) + ' seconds')
    print('--------------------------------')
    return

if __name__ == '__main__':
    # get correct data path if depending on current OS
    data_path = '/MARS/orig/supl/SHARAD/EDR/hebrus_valles_sn/'
    if os.getcwd().split('/')[1] == 'media':
        data_path = '/media/anomalocaris/Swaps' + data_path
    elif os.getcwd().split('/')[1] == 'mnt':
        data_path = '/mnt/d' + data_path
    else:
        print('Data path not found')
        sys.exit()
    chirp = 'calib'
    stackFac = 4            # stack factor - going with 4 to be safe and not incoherently stack
    beta = 0                # beta value for kaiser window [0 = rectangular, 5 	Similar to a Hamming, 6	Similar to a Hann, 8.6 	Similar to a Blackman]
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

    # uncomment for testing single obs., enter lbl file as sys.argv[1]
    # lbl_file = sys.argv[1]
    # lblName = data_path + lbl_file
    # runName = lbl_file.rstrip('_a.lbl')
    # auxName = data_path + runName + '_a_a.dat'
    # EDRName = data_path + runName + '_a_s.dat'
    # main(EDRName, auxName, lblName, chirp = chirp, stackFac = stackFac, beta = beta)

    for file in os.listdir(data_path):
        if file.endswith('.lbl'):
            lbl_file = file
            lblName = data_path + lbl_file
            runName = lbl_file.rstrip('_a.lbl')
            auxName = data_path + runName + '_a_a.dat'
            EDRName = data_path + runName + '_a_s.dat'
            
            if (not os.path.isfile(data_path + 'processed/data/geom/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_geom.csv')):
                main(EDRName, auxName, lblName, chirp = chirp, stackFac = stackFac, beta = beta)
            else :
                print('\n' + runName + ' already processed!\n')
