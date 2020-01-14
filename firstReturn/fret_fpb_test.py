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
    l = len(imarray)
    r = 3600
    c = len(imarray)/r
    imarray = imarray.reshape(r,c)

    #imarray = imarray[:,0:100:1]	#decrease the imarray to make testing faster

    (r,c) = imarray.shape   
    C = np.empty((r,c))	#create empty criteria array to localize surface echo for each trace
    gradient = np.gradient(imarray, axis = 0) #find gradient of each trace in RGRAM

    #criteria for surface echo - indicator is Pt * dPt-1/dt, 
    #where P is the signal energy applied on each grame sample (t)
    #indicator weights energy of a sample by the derivative preceding it

    for i in range(c):
            for j in range(r):
                    if j >= 100:
                            C[j,i] = imarray[j,i]*gradient[j-1,i]

    C_max = np.argmax(C, axis = 0)	#find indices of max critera seletor for each column
    fret_index = np.zeros((r,c))	#create empty fret index and power arrays
    fret_db = np.empty((c,1))

    #open geom nav file for rgram to append surface echo power to each trace
    (file_name, file_ext) = os.path.splitext(file)

    nav_file = np.genfromtxt('../..file_name.rstrip('rgram') + 'geom.tab', delimiter = ',', dtype = str)

    #nav_file = nav_file[0:100:1,:]	#decrease the imarray to make testing faster 
                    
    #iterate over the number of traces. add value to max criteria for each trace to create fret image
    #calculate power of first return for each trace
    for i in range(c):
            fret_index[C_max[i],i] = 255   #attach max criteria indices for each column to first return array - make white
            fret_db[i,:] = 10 * np.log10(imarray[C_max[i],i])

    #append fret values to a new column in geom.tab file. this should be the 11th column.
            #if fret has already been run and it is being re-run, overwrite 11th column
            #with new fret values
    #save new nav file as file_name.geom2.tab where fret is 11th column
    #also output individual fret .txt
    if nav_file.shape[1] == 10:
        nav_file = np.append(nav_file, fret_db, 1)

    else:
        nav_file[:,10] = fret_db[:,0]
        
    np.savetxt(file_name.rstrip('rgram') + 'geom2.tab', nav_file, delimiter = ',', newline = '\n', fmt= '%s')
    np.savetxt(file_name + '_fret_db.txt', fret_db, delimiter=',', newline = '\n', comments = '', header = 'PDB', fmt='%.8f')

    #convert RGRAM array and fret array to images and save
    fret_array = Image.fromarray(fret_index)
    scipy.misc.imsave(file_name + '_fret_array.jpg', fret_array)
    #imarray = Image.fromarray(imarray)
    #scipy.misc.imsave(file_name + '_imarray.jpg', imarray)

    #keep track of lines processed
    print('First return processing of rgram ' + str(file_name.rstrip('rgram_')) + ' done!')

main()
    
            

