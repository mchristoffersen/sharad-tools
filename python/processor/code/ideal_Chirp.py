# script for testing SHARAD ideal chirp

# import necessary libraries
import numpy as np
from scipy.signal import chirp as chirpGen
import matplotlib.pyplot as plt
import os, sys


dt = .0375e-6                               # sampling interval for 3600 real-values voltage samples
delay_window = 3600 * dt                    # window length for sampling frequency of 1/dt
sharad_pri = 1.0 / 700.28                   # pulse repition interval
fLow = 15.0e6                               # low frequency of SHARAD chirp, 15 MHz
fHigh = 25.0e6                              # high frequency of SHARAD chirp, 25 MHz
pLen = 85.05e-6                             # pulse length for chirp, 85.05 microseconds
nSamp = pLen / dt                           # number of samples in pulse length, with spacing of dt
chirpTime = np.arange(0,nSamp) * dt         # time array for length of pulse with samples at .0375microsec

# using signal.chirp 
synthChirp = np.zeros(3600, complex)
synthChirp[:int(nSamp)] = chirpGen(chirpTime, fLow, nSamp, fHigh, method = 'linear')
synthChirpFFT = np.fft.fft(synthChirp)

# manually creating chirp  
# this is how Matt's code is set up to create the ideal chirp 
fSlope = (fLow - fHigh) / pLen              # frequency slope over length of pulse      
arg = 2.0*np.pi*chirpTime*(fHigh+fSlope*chirpTime/2.0)
idealChirp = np.zeros(3600, complex)
idealChirp[:int(nSamp)] = np.sin(arg)
idealChirpFFT = np.fft.fft(idealChirp)

# Compare outputs of the two methods 
plt.subplot(2,2,1)
plt.plot(synthChirp)
plt.title('synthChirp')
plt.subplot(2,2,2)
plt.plot(idealChirp)
plt.title('idealChirp')
plt.subplot(2,2,3)
plt.plot(synthChirpFFT)
plt.title('synthChirpFFT')
plt.subplot(2,2,4)
plt.plot(idealChirpFFT)
plt.title('idealChirpFFT')
plt.show()