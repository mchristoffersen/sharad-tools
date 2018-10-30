#Function finds first return from radargram per method in Grima et al., 2012
#Author: Brandon S. Tober
#Created 30January2018

import os
from PIL import Image
import math
import numpy as np
import scipy.misc
        
def main():
        #keep count of the number of rgrams processed
        count = 0
        fret(file)
        count += 1
        print('First return of rgram #' + count + ' done!')

def fret(file_name): 
#file_name will be filled by for loop----for root,dirs,files in os.walk('PDS'):----for file in files:----if file.endswith('.img):----fret(file)
      
        #convert binary .img PDS RGRAM to numpy array. Reshape array with 3600 lines
        dtype = np.dtype('float32')     
        file = open(root + file_name +'_rgram.img', 'rb') 
        imarray = np.fromfile(file, dtype)     
        l = len(imarray)
        c = 3600
        imarray = imarray.reshape(c,l/c)

        #print(imarray.shape)

        #imarray = imarray[:,0:100:1]	#decrease the imarray to make testing faster

        (r,c) = imarray.shape   
        C = np.empty((r,c))	#create empty criteria array to localize surface echo for each trace
        gradient = np.gradient(imarray, axis = 0) #find gradient of each trace in RGRAM

        #criteria for surface echo - indicator is Pt * dPt-1/dt, 
        #where P is the signal energy applied on each grame sample (t). Indicator weights
        #energy of a sample by the derivative preceding it.

        for i in range(c):
                for j in range(r):
                        if j >= 1:
                                C[j,i] = imarray[j,i]*gradient[j-1,i]

        C_max = np.argmax(C, axis = 0)	#find indices of max critera seletor for each column
        fret_index = np.zeros((r,c))	#create empty fret index and power arrays
        fret_db = np.empty((c,1))

        #open geom nav file for rgram to append surface echo power to each trace
        (head,tail) = os.path.split(root)
        nav_file = np.genfromtxt(path + '/data/geom/' + tail + '/' + file_name + '_geom.tab', delimiter = ',', dtype = str)

        #nav_file = nav_file[0:100:1,:]	#decrease the imarray to make testing faster 
                        
        #iterate over the number of traces. add value to max criteria for each trace to create fret image
        #calculate power of first return for each trace
        for i in range(c):
                fret_index[C_max[i],i] = 255   #attach max criteria indices for each column to first return array - make white
                fret_db[i,:] = np.log10(imarray[C_max[i],i])*10

        #append fret values to a new column in geom.tab file and save over original .tab file. also output individual fret .txt
        nav_file = np.append(nav_file, fret_db, 1)
        np.savetxt(file_name + '_geom.tab', nav_file, delimiter = ',', newline = '\n', fmt= '%s')
        np.savetxt(file_name + '_fret_db.txt', fret_db, delimiter=',', newline = '\n', comments = '', header = 'PDB', fmt='%.8f')

        #convert RGRAM array and fret array to images and save
        fret_array = Image.fromarray(fret_index)
        scipy.misc.imsave(file_name + '_fret_array.jpg', fret_array)
        imarray = Image.fromarray(imarray)
        scipy.misc.imsave(file_name + '_imarray.jpg', imarray)

#call the main function
main()
        
