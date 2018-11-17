# Import necessary libraries
import numpy as np
import scipy
import matplotlib.pyplot as plt
import glob, os, sys, time
from lbl_Parse import lbl_Parse
from aux_Parse import aux_Parse
from anc_Parse import anc_Parse
from read_Chirp import ref_Chirp
from rgram import rgram
from read_EDR import EDR_Parse, sci_Decompress



def main(EDRName, auxName, lblName, chirp = 'synth', presumFac = None):
    """
    This python script is used to pulse compress raw SHARAD EDRs to return chirp compressed science record. Output should be complex voltage.

    Much of this code was adapted from Matthew Perry's FrankenRDR work, along with Michael Chrostoffersen's sharad-tools. Cetain packages were directly updated from their work (ie. readLBL, readAnc, readAux). This code simply aims to pulse compress the raw data, without performing any other processing steps.

    github: b-tober

    Written by: Brandon S. Tober
    Date: 23Aug2018

    Example call:
    EDRName = '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a_s.dat'

    auxName =  '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a_a.dat'

    lblName =  '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/edr_test/e_5050702_001_ss19_700_a.lbl'

    chirp = 'cal'

    main(EDRName, auxName, lblName, chirp)
    """
    t0 = time.time()                    #start time
    print('--------------------------------')
    print(runName)
    print('--------------------------------')

    # extract relecant information from lbl file
    print('Reading label file...')
    lblDic = lbl_Parse(lblName)
    records = lblDic['FILE_RECORDS']    # number of records in observation (traces)
    instrPresum = lblDic['INSTR_MODE_ID']['Presum']       # onboard presums
    instrMode = lblDic['INSTR_MODE_ID']['Mode']
    BitsPerSample = lblDic['INSTR_MODE_ID']['BitsPerSample']

    # downsize option for testing purposes
    #records = int(records / 1000)


    # presumming is just for visualization purposes
    presumFac = 8
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

    # determine average TX and RX temps if using Italian reference chirp
    txTemp = np.mean(auxDF['TX_TEMP'][:])
    rxTemp = np.mean(auxDF['RX_TEMP'][:])
    
    # set up empty data arrays to hold Output
    if chirp =='ideal' or chirp == 'UPB':
        EDRData = np.zeros((3600,records), complex)
        EDRData_presum = np.zeros((3600, presumCols), complex)
    elif chirp == 'calib':
        EDRData = np.zeros((2048,records), complex)
        EDRData_presum = np.zeros((2048, presumCols), complex)        
    geomData = np.zeros((records,5))

    #
    # begin opening data and processing
    #
    # read in reference chirp
    refChirp = ref_Chirp(chirp, txTemp, rxTemp)
    print('Reference chirp opened' + ' (type = ' +  chirp + ')')
    # plt.subplot(3,1,1)
    # plt.plot(np.fft.ifft(refChirp))
    # plt.subplot(3,1,2)
    # plt.plot(np.real(np.fft.ifft(refChirp)))
    # plt.subplot(3,1,3)
    # plt.plot(np.imag(np.fft.ifft(refChirp)))
    # plt.show()
    # sys.exit()

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
    # begin pulse compression steps
    n = np.arange(records)
    if chirp =='calib':
        refChirp_conj = np.conj(refChirp)                          # Take the complex conjugate of the reference chirp
        fc = (20.-(80./3.))*1e6                                    #-6.66 MHz
        dt = (3./80.)*1e-6                                           # 0.0375 Microseconds
        t = np.arange(0*dt, 4096*dt, dt)
        phase_shift = np.exp(2*np.pi*1j*fc*t)                    #right shift spectrum when multiplied by zero padded raw data

        #for _i in range(records):
        # check length of the science data
        sciPad = np.zeros((4096,records), complex)
        sciPad[:len(sci[:,n]),n] = sci[:,n]
    
        # shift the data to the right by 6.66 MHz
        sciShift = sciPad * phase_shift[:,np.newaxis]
        sciFFT = np.fft.fft(sciShift, axis = 0) / sciShift.shape[0]
        # place spectrum in natural ordering
        sciFFT = np.fft.fftshift(sciFFT, 0)


        # take central 2048 samples
        st = 1024
        en = 3072
        sciFFT_cut = sciFFT[st:en,n]

        # perform chirp compression
        dechirpData = sciFFT_cut * refChirp_conj[:,np.newaxis]

        # Inverse Fourier transfrom and fix scaling
        EDRData = np.fft.ifft(dechirpData, axis = 0)  * dechirpData.shape[0]


    else:
        # flip reference chirp
        #refChirpFlip = np.flipud(refChirp)

        # take complex conjugate of reference chirp fourier transform
        refChirpComp = np.conj(refChirp)

        #for _i in range(records):
        # Fourier transform of data
        sciFFT = np.fft.fft(sci[:,n]) / sci.shape[0]

        # multiple Fourier transform of reference chip by that of the data
        dechirpData = sciFFT[:,n] * refChirpComp

        # Inverse Fourier transform of dechirped data to place back in time domain
        EDRData = np.fft.ifft(dechirpData[:,n]) * sci.shape[0]
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

    # Convert complex-values voltage return to amplitude scaled by max value
    pow_out = np.power(np.real(EDRData), 2)
    print(pow_out[0:50,0])
    print(10*np.log10(pow_out[0:50,1]/1e-3))
    #sys.exit()
    #EDRData_presum_pow = np.power(np.real(EDRData_presum), 2)

    # create radargrams from presummed data to visualize output, also save data
    rgram(EDRData_presum, data_path, runName + '_' + chirp, rel = True)
    np.savetxt(data_path + 'processed/data/geom/' + runName + '_geom.csv', geomData, delimiter = ',', newline = '\n',fmt = '%s')
    np.save(data_path + 'processed/data/rgram/comp/' + runName + '_comp.npy', EDRData)
    np.save(data_path + 'processed/data/rgram/' + runName + '_pow.npy', pow_out)
    t1 = time.time()    # End time
    print('--------------------------------')
    print('Total Runtime: ' + str(round((t1 - t0),4)) + ' seconds')
    print('--------------------------------')
    return

if __name__ == '__main__':
    data_path = '/media/anomalocaris/Swaps/Google_Drive/MARS/orig/supl/SHARAD/EDR/edr_test/'
    lbl_file = sys.argv[1]
    lblName = data_path + lbl_file
    runName = lbl_file.rstrip('_a.lbl')
    auxName = data_path + runName + '_a_a.dat'
    EDRName = data_path + runName + '_a_s.dat'
    chirp = 'calib'
    presumFac = 8           # presum factor for radargram visualization; data is not presummed
    # if (not os.path.isfile(data_path + 'processed/data/geom/' + runName + '_geom.csv')):
    main(EDRName, auxName, lblName, chirp = chirp, presumFac = presumFac)
    # else :
    #     print('\n' + runName.split('_')[1] + runName.split('_')[2] + ' already processed!\n')
