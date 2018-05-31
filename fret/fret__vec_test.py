#script finds first return from radargram per method in Grima et al., 2012
#this is a test first return script
#run single input .img rgram as argument to fret.py
#while in same directory as rgram and geom file for fret values to be appended to
#example run command: python fret_test.py s_00224201_rgram.img
#author: Brandon S. Tober
#created 30January2018

import os
import sys
from PIL import Image
import math
import numpy as np
import scipy.misc
import time

def main():
    
    #.img file is given as argument
    file = sys.argv[1] 
    print('\n----------------------------------------------------------------')

    #convert binary .img PDS RGRAM to numpy array
    #reshape array with 3600 lines
    dtype = np.dtype('float32')     
    rgram = open(file, 'rb') 
    imarray = np.fromfile(rgram, dtype)
    print(file + ' loaded')
    l = len(imarray)
    r = 3600
    c = len(imarray)/r
    print(r,c)
    imarray = imarray.reshape(r,c)

    imarray = imarray[:,0:100:1]	#decrease the imarray to make testing faster

    (r,c) = imarray.shape   
    C = np.zeros((r,c))	    #create empty criteria array to localize surface echo for each trace
    C2 = np.zeros((r,c))

    gradient = np.gradient(imarray, axis = 0)   #find gradient of each trace in RGRAM
    print('gradient computed')

    #criteria for surface echo - indicator is Pt * dPt-1/dt, 
    #where P is the signal energy applied on each grame sample (t)
    #indicator weights energy of a sample by the derivative preceding it
    t0 = time.time()
    for i in range(c):
        for j in range(r):
            if j >= 100:
                C[j,i] = imarray[j,i]*gradient[j-1,i]
    t1 = time.time()
    
    C2[100:r,:] = imarray[100:r,:]*gradient[99:r-1,:]
    t2 = time.time()
    
    print(C == C2)
    print('Loop time: ' + str(t1 - t0) + ' seconds')
    print('Vectorized time: ' + str(t2 - t1) + ' seconds')


    C_max_ind = np.argmax(C, axis = 0)	#find indices of max critera seletor for each column
    C2_max_ind = np.argmax(C2, axis = 0)	#find indices of max critera seletor for each column

    C_max = np.amax(C, axis = 0)        #find the max criteria value 
    C_2_max = np.amax(C2, axis = 0)

    #print(C_max_ind.shape)
    #print(C2_max_ind.shape)
    #print(C_max_ind == C2_max_ind)

    fret_index = np.zeros((r,c))	#create empty fret index and power arrays
    fret_index2 = np.zeros((r,c))

    fret_db = np.zeros((c,1))
    fret_db2 = np.zeros(c)
    
    #iterate over the number of traces. add value to max criteria for each trace to create fret image
    #calculate power of first return for each trace
    for i in range(c):
        fret_index[C_max_ind[i],i] = 255   #attach max criteria indices for each column to first return array - make white
        fret_db[i,0] = np.log10(imarray[C_max_ind[i],i])*10

    #print(fret_db.shape)
    #print(fret_db)
    
    fret_index2[C2_max_ind[:],:] = 255
    #print(fret_index == fret_index2)
    #print(C2_max[0:c:1].shape)
    
    #fret_db2 = np.log10(imarray[0:C2_max[0:c-1],:r])*10

    condition = fret_index2 == 255
    #print(condition.shape)
    #print(imarray.shape)
    #print(condition)

    #print(len(imarray[condition]))
    surf = imarray[condition]
    #print(surf.shape)
    #print(surf)
    #fret_db2 = np.log10(surf)*10

    #fret_db2 = np.log10(np.take(imarray, C_max))*10

    #fret_db2[:] = np.log10(imarray[C_max[:],:])*10
    #print(fret_db2.shape)
    #print(fret_db2)
    #print(fret_db == fret_db2)

main()
    
            

