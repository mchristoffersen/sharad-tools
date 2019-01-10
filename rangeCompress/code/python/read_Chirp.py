# import necessary libraries
import numpy as np
from scipy.signal import chirp as chirpGen
import matplotlib.pyplot as plt
import os, sys


def open_Chirp(chirp, TxTemp, RxTemp):
    """
    This function is used to read in a variety of reference chirp options for SHARAD pulse compression. 
    This was modified from Matt Perry's FrankenRDR readChirp function

    Updated by: Brandon S. Tober
    Last updated: 17Nov2018
    """

    if chirp == 'calib':
        calChirpFile = []
        calibRoot = '../../calib/'
        calibName = 'reference_chirp'
        ext = '.dat'
        TxCalNames = ['m20tx', 'm15tx', 'm10tx', 'm05tx',
                      'p00tx', 'p20tx', 'p40tx', 'p60tx']
        RxCalNames = ['m20rx', 'p00rx', 'p20rx', 'p40rx',
                      'p60rx']

        Tx = [-20, -15, -10, -5, 0, 20, 40, 60]
        Rx = [-20, 0, 20, 40, 60]
        #
        # Define vectors for Tx and Rx temps
        #
        for _i in range(len(TxTemp)):

            TxDiff = []#np.zeros(len(TxTemp))
            RxDiff = []#np.zeros(len(TxTemp))
            #
            # Find distance
            #
            TxDiff = [abs(x - TxTemp[_i]) for x in Tx]
            RxDiff = [abs(x - RxTemp[_i]) for x in Rx]
            #
            # Find the indices of the closest Tx and Rx value
            #
            #calibTx = TxCalNames[TxDiff.index(min(TxDiff))]
            #calibRx = RxCalNames[RxDiff.index(min(RxDiff))]
            #
            # Construct File name
            #
            calChirpFile = calChirpFile + [str(calibRoot + calibName + '_' + \
                        TxCalNames[TxDiff.index(min(TxDiff))] + '_' + \
                        RxCalNames[RxDiff.index(min(RxDiff))] + ext)]

        #get the unique chirps required for compression
        calChirpFilesUnique = list(set(calChirpFile))
        
        calChirps = np.empty((len(calChirpFilesUnique),2048), dtype = 'complex64')

        for _i in range(len(calChirpFilesUnique)):
            if os.path.isfile(calChirpFilesUnique[_i]):
                calChirp = np.fromfile(calChirpFilesUnique[_i], dtype='<f')
                real = calChirp[:2048]
                imag = calChirp[2048:]
                calChirp = real + 1j*imag
                calChirpConj = np.conj(calChirp)
                calChirps[_i,:] = calChirpConj[:]

            else:
                print('Calibrated chirp file not found...exiting.')
                sys.exit()

        # create list with indices to required reference chirp for each trace in radar data
        calChirpFiles = [calChirpFilesUnique.index(_i) for _i in calChirpFile]   

        return calChirps, calChirpFiles

    elif chirp == 'ideal' or chirp == 'synth' or chirp == 'UPB':
    
        # ideal chirp from UPB
        dt = .0375e-6                               # sampling interval for 3600 real-values voltage samples
        delay_window = 3600 * dt                    # window length for sampling frequency of 1/dt
        sharad_pri = 1.0 / 700.28                   # pulse repition interval
        fLow = 15.0e6                               # low frequency of SHARAD chirp, 15 MHz
        fHigh = 25.0e6                              # high frequency of SHARAD chirp, 25 MHz
        beta = fHigh - fLow                         # bandwidth of chirp
        pLen = 85.05e-6                             # pulse length for chirp, 85.05 microseconds
        nSamp = pLen / dt                           # number of samples in pulse length, with spacing of dt
        fSlope = (fLow - fHigh) / pLen              # frequency slope over length of pulse
        chirpTime = np.arange(0,nSamp) * dt         # time array for length of pulse with samples at .0375microsec        
        arg = 2.0*np.pi*chirpTime*(fHigh+fSlope*chirpTime/2.0)
        idealChirp = np.zeros(3600, complex)
        idealChirp[:int(nSamp)] = np.sin(arg)       # trying to determine whether to use sine-wave generator or cosine - scipy.signal.chirp uses cosine
        idealChirpFFT = np.fft.fft(idealChirp)
        idealChirpConj = np.conj(idealChirpFFT)

        if chirp == 'ideal':
            return idealChirpConj

        # synthetic chirp using scipy.signal chirp generator - this should be the same as the above chirp method
        synthChirp = np.zeros(3600, complex)
        synthChirp[:int(nSamp)] = chirpGen(chirpTime, fHigh, pLen, fLow, method = 'linear')
        synthChirpFFT = np.fft.fft(synthChirp)
        synthChirpConj = np.conj(synthChirpFFT)
                
        if chirp == 'synth':
            return synthChirpConj
        
        elif chirp == 'UPB':
            
            # load cal_filter.dat
            cal_filter = np.fromfile('../../calib/cal_filter.dat', '<f')
            cal_filter = cal_filter[:1800] + 1j*cal_filter[1800:]
            cal_filter = np.roll(cal_filter, 900)
            calChirp = np.zeros(3600, complex)
            calChirp[1800:] = cal_filter
            calChirp = calChirp*idealChirpFFT
            calChirpConj = np.conj(calChirp)
            return calChirpConj

    else:
        print('Unknown reference chirp type')
        sys.exit()

