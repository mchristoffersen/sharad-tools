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



def main(EDRName, auxName, lblName, chirp = 'synth', presumFac = None):
    """
    This python script is used to pulse compress raw SHARAD EDRs to return chirp compressed science record. Output should be complex voltage.

    This code was adapted from Matthew Perry's FrankenRDR work, along with Michael Chrostoffersen's sharad-tools. Certain packages were directly updated from their work (ie. readLBL, readAnc, readAux). This code simply aims to pulse compress the raw data, without performing any other processing steps.

    github: b-tober

    Updated by: Brandon S. Tober
    Date: 23Aug2018

    Example call:
    EDRName = '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a_s.dat'

    auxName =  '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a_a.dat'

    lblName =  '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a.lbl'

    chirp = 'calib'

    presumFac = 8

    main(EDRName, auxName, lblName, chirp = chirp, presumFac = presumFac)
    """
    t0 = time.time()                    #start time
    print('--------------------------------')
    print(runName)
    print('--------------------------------')
    print(lblName)

    # extract relecant information from lbl file
    print('Reading label file...')
    lblDic = lbl_Parse(lblName)
    records = lblDic['FILE_RECORDS']    # number of records in observation (traces)
    instrPresum = lblDic['INSTR_MODE_ID']['Presum']       # onboard presums
    instrMode = lblDic['INSTR_MODE_ID']['Mode']
    BitsPerSample = lblDic['INSTR_MODE_ID']['BitsPerSample']

    # downsize option for testing purposes
    #records = int(records / 100)


    # presumming is just for visualization purposes
    presumCols = int(np.ceil(records/presumFac))

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
    print('---- Begin Processing ----')

    # determine TX and RX temps if using Italian reference chirp
    txTemp = auxDF['TX_TEMP'][:]
    rxTemp = auxDF['RX_TEMP'][:]
    
    # set up empty data arrays to hold Output
    if chirp =='ideal' or chirp == 'synth' or chirp == 'UPB':
        EDRData = np.zeros((3600,records), complex)
        EDRData_presum = np.zeros((3600, presumCols), complex)
    elif chirp == 'calib':
        EDRData = np.zeros((2048,records), complex)
        EDRData_presum = np.zeros((2048, presumCols), complex)        
    geomData = np.zeros((records,5))

    # read in reference chirp as matched filter - this should be imported in Fourier frequency domain, as complex conjugate
    refChirpMF = open_Chirp(chirp, txTemp, rxTemp)
    print('Reference chirp opened' + ' (type = ' +  chirp + ')')


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
    # begin range compression 
    if chirp =='calib':
        fc = (20.-(80./3.))*1e6                                    #-6.66 MHz
        dt = (3./80.)*1e-6                                           # 0.0375 Microseconds
        t = np.arange(0*dt, 4096*dt, dt)
        phase_shift = np.exp(2*np.pi*1j*fc*t)                    #right shift spectrum when multiplied by zero padded raw data

        for _i in range(records):
            # check length of the science data
            sciPad = np.zeros(4096, complex)
            sciPad[:len(sci[:,_i])] = sci[:,_i]

        
            # shift the data to the right by 6.66 MHz
            sciShift = sciPad * phase_shift
            sciFFT = np.fft.fft(sciShift)# / len(sciShift)
            # place spectrum in natural ordering
            sciFFT = np.fft.fftshift(sciFFT)
    

            # take central 2048 samples
            st = 1024
            en = 3072
            sciFFT_cut = sciFFT[st:en]

            # perform chirp compression
            dechirpData = sciFFT_cut * refChirpMF

            # Inverse Fourier transfrom and fix scaling
            EDRData[:,_i] = np.fft.ifft(dechirpData)#  * dechirpData.shape[0]
    else:

        for _i in range(records):
            # fourier transform of data
            sciFFT = np.fft.fft(sci[:,_i])# / len(sci[:,_i])

            # multiple Fourier transform of reference chip by that of the data
            dechirpData = sciFFT * refChirpMF

            # inverse fourier transform of dechirped data to place back in time domain
            EDRData[:,_i] = np.fft.ifft(dechirpData)# * len(sci[:,_i])
    print('Pulse compression complese')

    # presum data by factor or eight for visualization purposes
    for _i in range(presumCols - 1):
        EDRData_presum[:,_i] = np.mean(EDRData[:,presumFac*_i:presumFac*(_i+1)], axis = 1)

    # account for traces left if number of traces is not divisible by presumFac
    EDRData_presum[:,-1] = np.mean(EDRData[:,presumFac*(_i+1):-1], axis = 1)
    print('Presumming complete')

    # create geom array with relavant data for each record
    for _i in range(records):
        geomData[_i,0] = runName.split('_')[1]
        geomData[_i,1] = int(_i)
        geomData[_i,2] = auxDF['SUB_SC_PLANETOCENTRIC_LATITUDE'][_i]
        geomData[_i,3] = auxDF['SUB_SC_EAST_LONGITUDE'][_i]
        geomData[_i,4] = auxDF['SOLAR_ZENITH_ANGLE'][_i]

    # convert complex-valued voltage return to power values
    BruceData = np.fromfile('../../../../../orig/supl/SHARAD/EDR/EDR_pc_bruce/592101000_1_Unif_SLC.raw', dtype = 'complex64')
    BruceData = BruceData.reshape(3600, int(len(BruceData)/3600))
    #print(BruceData)
    ampOut = np.abs(EDRData)
    print(ampOut)
    print(np.abs(BruceData))
    #print(ampOut)
    #print(np.divide(EDRData,BruceData))
    plt.subplot(4,1,1)
    plt.plot(np.abs(np.divide(EDRData,BruceData)[:,1000]))
    plt.subplot(4,1,2)
    plt.plot(np.abs(np.divide(EDRData,BruceData)[:,10000]))
    plt.subplot(4,1,3)
    plt.plot(np.abs(np.divide(EDRData,BruceData)[:,15000]))
    plt.subplot(4,1,4)
    plt.plot(np.abs(np.divide(EDRData,BruceData)[:,24000]))
    plt.show()
    sys.exit()

    # create radargrams from presummed data to ../../orig/supl/SHARAD/EDR/EDR_pc_brucevisualize output, also save data
    rgram(EDRData[:1800,::32], data_path, runName + '_' + chirp, rel = True)
    np.savetxt(data_path + 'processed/data/geom/' + runName + '_' + chirp + '_geom.csv', geomData, delimiter = ',', newline = '\n',fmt = '%s')
    np.save(data_path + 'processed/data/rgram/comp/' + runName + '_' + chirp + '_comp.npy', EDRData)
    np.save(data_path + 'processed/data/rgram/' + runName + '_' + chirp + '_amp.npy', ampOut)

    t1 = time.time()    # End time
    print('--------------------------------')
    print('Total Runtime: ' + str(round((t1 - t0),4)) + ' seconds')
    print('--------------------------------')
    return

if __name__ == '__main__':
    data_path = /MARS/orig/supl/SHARAD/EDR/edr_test/
    if os.getwd().split('/')[1] = 'media':
        data_path = '/media/anomalocaris/Swaps' + data_path
    elif os.getwd().split('/')[1] = 'mnt':
        data_path = '/mnt/d' + data_path
    else:
        print('Data path not found')
        sys.exit()
    lbl_file = sys.argv[1]
    lblName = data_path + lbl_file
    runName = lbl_file.rstrip('_a.lbl')
    auxName = data_path + runName + '_a_a.dat'
    EDRName = data_path + runName + '_a_s.dat'
    chirp = 'synth'
    presumFac = 8           # presum factor for radargram visualization; actual data is not presummed
    #if (not os.path.isfile(data_path + 'processed/data/geom/' + runName + '_geom.csv')):
    main(EDRName, auxName, lblName, chirp = chirp, presumFac = presumFac)
    #else :
    #    print('\n' + runName.split('_')[1] + runName.split('_')[2] + ' already processed!\n')
