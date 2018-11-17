# script for testing SHARAD ideal chirp methods for pulse compression

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
beta = fHigh - fLow                         # bandwidth of chirp
pLen = 85.05e-6                             # pulse length for chirp, 85.05 microseconds
nSamp = pLen / dt                           # number of samples in pulse length, with spacing of dt
chirpTime = np.arange(0,nSamp) * dt         # time array for length of pulse with samples at .0375microsec

# using signal.chirp 
synthChirp = np.zeros(3600, complex)
synthChirp[:int(nSamp)] = chirpGen(chirpTime, fHigh, pLen, fLow, method = 'linear')
synthChirpFFT = np.fft.fft(synthChirp)
synthChirpConj = np.conj(synthChirpFFT)

# synthetic chirp using LFM waveform complex exponential, x_t = exp(pi*j*beta/tau*t^2)
j = np.sqrt([-1],dtype = complex)
synthChirpBase = np.zeros(3600, complex)
synthChirpBase[:int(nSamp)] = np.exp(np.pi*j*(beta/pLen)*np.power(chirpTime,2))
synthChirpBaseFFT = np.fft.fft(synthChirpBase)
synthChirpBaseConj = np.conj(synthChirpBaseFFT)

# manually creating chirp  
# this is how Matt's code is set up to create the ideal chirp 
fSlope = (fLow - fHigh) / pLen              # frequency slope over length of pulse      
arg = 2.0*np.pi*chirpTime*(fHigh+fSlope*chirpTime/2.0)
idealChirp = np.zeros(3600, complex)
idealChirp[:int(nSamp)] = np.sin(arg)
idealChirpFFT = np.fft.fft(idealChirp)
idealChirpConj = np.conj(idealChirpFFT)


# import one of the italian reference chirps to compare with ideal/synth chirp
calChirp = np.fromfile('../../calib/reference_chirp_p20tx_p20rx.dat', dtype='<f')
real = calChirp[:2048]
imag = calChirp[2048:]
calChirp = real + 1j*imag
calChirpConj = np.conj(calChirp)

# load cal_filter.dat
calFilter = np.fromfile('../../calib/cal_filter.dat', '<f')
calFilter = calFilter[:1800] + 1j*calFilter[1800:]
calFilter = np.roll(calFilter, 900)
UPBChirp = np.zeros(3600, complex)
UPBChirp[1800:] = calFilter
UPBChirp = UPBChirp*idealChirpFFT
UPBChirpConj = np.conj(idealChirpFFT)

# Compare outputs

plt.subplot(2,1,1)
plt.plot(idealChirp)
plt.plot(synthChirp)
plt.subplot(2,1,2)
plt.plot(np.divide(idealChirp,synthChirp))
plt.show()

plt.subplot(2,3,1)
plt.plot(synthChirp)
plt.title('synthChirp')
plt.subplot(2,3,2)
plt.plot(idealChirp)
plt.title('idealChirp')
plt.subplot(2,3,4)
plt.plot(synthChirpConj)
plt.title('synthChirpConj')
plt.subplot(2,3,5)
plt.plot(idealChirpConj)
plt.title('idealChirpCOnj')
plt.subplot(2,3,3)
plt.plot(np.fft.ifft(calChirp))
plt.title('calChirp IFFT')
plt.subplot(2,3,6)
plt.plot(calChirp)
plt.plot(calChirpConj)
plt.title('calChirpConj')
plt.show()

plt.subplot(2,2,1)
plt.plot(synthChirpFFT)
plt.title('synthChirpFFT')
plt.subplot(2,2,2)
plt.plot(synthChirpBaseFFT)
plt.title('synthChirpBaseFFT')
plt.subplot(2,2,3)
plt.plot(np.fft.fftshift(synthChirpFFT))
plt.title('synthChirpFFT shift')
plt.subplot(2,2,4)
plt.plot(np.fft.fftshift(synthChirpBaseFFT))
plt.title('synthChirpBaseFFT shift')
plt.show()

plt.subplot(4,1,1)
plt.plot(np.real(synthChirp))
plt.title('abs synth')
plt.subplot(4,1,2)
plt.plot(np.imag(synthChirp))
plt.title('imag synth')
plt.subplot(4,1,3)
plt.plot(np.real(synthChirpBase))
plt.title('real synthBase')
plt.subplot(4,1,4)
plt.plot(np.imag(synthChirpBase))
plt.title('abs synthBase')
plt.show()

plt.subplot(3,1,1)
plt.plot(calFilter)
plt.title('UPB cal chirp filter')
plt.subplot(3,1,2)
plt.plot(idealChirpFFT)
plt.title('ideal chirp FFT')
plt.subplot(3,1,3)
plt.plot(UPBChirp)
plt.title('calibrated UPB chirp FFT')
plt.show()