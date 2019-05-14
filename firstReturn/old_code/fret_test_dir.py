#script finds first return from radargram per method in Grima et al., 2012.
#this will run through all .img radargrams in directory.
#designed to run on directory structured like the PDS.
#author: Brandon S. Tober
#created 30January2018

import os, sys
from PIL import Image
import math
import numpy as np
import scipy.misc
import time

def main():
    
    #set path of directory
    path = '/media/anomalocaris/Swaps/Google_Drive/MARS/code/sharad-tools/python/fret/fret_test'
    print(path)
    print('\n----------------------------------------------------------------')

    #keep count of the number of rgrams processed
    count = 0       

    t0 = time.time()    #start time
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('0592101_rgram.img'):
                print(file)
                #convert binary .img PDS RGRAM to numpy array
                #reshape array with 3600 lines
                dtype = np.dtype('float32')
                rgram = open(root + '/' + file, 'rb') 
                imarray = np.fromfile(rgram, dtype)
                l = len(imarray)
                r = 3600
                c = len(imarray)//r
                print(c)
                imarray = imarray.reshape((r,c))

                #imarray = imarray[:,0:100:1]	#decrease the imarray to make testing faster

                (r,c) = imarray.shape   
                C = np.empty((r,c))	#create empty criteria array to localize surface echo for each trace
                gradient = np.gradient(imarray, axis = 0) #find gradient of each trace in RGRAM

                #criteria for surface echo - indicator is Pt * dPt-1/dt, 
                #where P is the signal energy applied on each grame sample (t)
                #Indicator weights energy of a sample by the derivative preceding it

                for i in range(c):
                    for j in range(r):
                        if j >= 100:
                            C[j,i] = imarray[j,i]*gradient[j-1,i]

                C_max = np.argmax(C, axis = 0)	#find indices of max critera seletor for each column
                fret_index = np.zeros((r,c))	#create empty fret index and power arrays
                fret_db = np.empty((c,1))

                #open geom nav file for rgram to append surface echo power to each trace
                (file_name, file_ext) = os.path.splitext(file)
                
                (head,tail) = os.path.split(root)
                
                nav_file = np.genfromtxt(path + '/data/geom/' + tail + '/' + file_name.rstrip('rgram') + 'geom.tab', delimiter = ',', dtype = str)

                #nav_file = nav_file[0:100:1,:]	#decrease the imarray to make testing faster 
                                
                #iterate over the number of traces. add value to max criteria for each trace to create fret image
                #calculate power of first return for each trace
                for i in range(c):
                    fret_index[C_max[i],i] = 255   #attach max criteria indices for each column to first return array - make white
                    fret_db[i,:] = 10 * np.log10(imarray[C_max[i],i])
                print(imarray)
                sys.exit()

                #append fret values to a new column in geom.tab file. this should be the 11th column
                        #if fret has already been run and it is being re-run, overwrite 11th column
                        #with new fret values
                #save new nav file as file_name.geom2.tab where fret is 11th column
                #also output individual fret .txt
                if nav_file.shape[1] == 10:
                    nav_file = np.append(nav_file, fret_db, 1)

                else:
                    nav_file[:,10] = fret_db[:,0]
                    
                np.savetxt(path + '/data/geom/' + tail + '/' + file_name.rstrip('rgram') + 'geom2.tab', nav_file, delimiter = ',', newline = '\n', fmt= '%s')
                np.savetxt(root + '/' + file_name + '_fret_db.txt', fret_db, delimiter=',', newline = '\n', comments = '', header = 'PDB', fmt='%.8f')

                #convert RGRAM array and fret array to images and save
                fret_array = Image.fromarray(fret_index)
                scipy.misc.imsave(root + '/' + file_name + '_fret_array.jpg', fret_array)
                
                #update the counter to keep track of lines processed
                count += 1
                print('First return processing of rgram #' + str(count) + '; ' + file + ' done!')
            else:
                print('No .img radargrams found')

    t1 = time.time()    #end time
    print('Total Runtime: ' + str((t1 - t0)/60) + ' minutes')

#call the main function
main()
        
