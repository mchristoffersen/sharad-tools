#script finds first return from radargram per method in Grima et al., 2012.
#this will run through all .img radargrams in directory.
#designed to run on directory structured like the PDS.
#author: Brandon S. Tober
#created 30January2018

import os
from PIL import Image
import math
import numpy as np
import scipy.misc
import time

def main():
    
    #set path of directory
    in_path = '/disk/qnap-2/MARS/orig/supl/SHARAD/EDR/bh_nh_bt/processed/data/'
    out_path = '/disk/qnap-2/MARS/targ/xtra/rsr/bh_nh_bt/EDR/fret/'
    print('\n----------------------------------------------------------------')

    #keep count of the number of rgrams processed
    count = 0       

    # overall start time
    t0 = time.time()                                                
    files =  os.listdir(in_path + 'rgram/')
    for file in files:
        if file.endswith('amp.npy'):
            if (not os.path.isfile(out_path + file.rstrip('amp.npy') + '.geom2.csv')):
                # start time for current line
                t1 = time.time()                                    
                print(file)
                file_number = file.split('_')[1] + file.split('_')[2]
                #load the binary nupy array of real-valued amplitudes
                imarray = np.load(in_path + 'rgram/' + file)
                (r,c) = imarray.shape
                
                #decrease the imarray to make testing faster
                #imarray = imarray[:,0:100:1]	

                #create empty criteria array to localize surface echo for each trace
                C = np.zeros((r,c))
                
                #find gradient of each trace in RGRAM
                gradient = np.gradient(imarray, axis = 0) 

                #criteria for surface echo - indicator is Pt * dPt-1/dt, 
                #where P is the signal energy applied on each grame sample (t)
                #Indicator weights energy of a sample by the derivative preceding it

                #for i in range(c):
                    #for j in range(r):
                        #while j >= 100:
                            #C[j,i] = imarray[j,i]*gradient[j-1,i]

                #vectorized criteria calculation
                C[100:r,:] = imarray[100:r,:]*gradient[99:r-1,:]    

                #find indices of max critera seletor for each column
                C_max_ind = np.argmax(C, axis = 0)
                
                #create empty fret index and power arrays
                fret_index = np.zeros((r,c))
                fret_amp = np.zeros((c,1))
                fret_db = np.zeros((c,1))

                #open geom nav file for rgram to append surface echo power to each trace
                nav_file = np.genfromtxt(in_path + 'geom/' + file.rstrip('_amp.npy') + '_geom.csv', delimiter = ',', dtype = str)

                #decrease the imarray to make testing faster 
                #nav_file = nav_file[0:100:1,:]	
                                
                #iterate over the number of traces. add value to max criteria for each trace to create fret image
                #calculate power of first return for each trace
                #for i in range(c):
                    #attach max criteria indices for each column to first return array - make white
                    #fret_index[C_max[:],:] = 255  

                    #account for slope between two accompanying indices to avoid stray mispicks
                    #choose next C_max for each column until slope is less than... tolerance
                    #this will keep choosing the a new C_max index for each trace until
                    #the slope between this trace fret and that of the previous trace is less than the tolerance
                    #while i > 0:
                        #print(np.abs(C_max[i - 1] - C_max[i]))
                        #if np.abs(C_max[i - 1] - C_max[i]) > 5:
                            #C_max[i] = np.argmax(C[:,i] < C_max[i])
                            #print(C_max[i])

                    #fret_db[i,:] = np.log10(imarray[C_max[i],i])*10

                #vectirized first return array and first return power out
                #attach max criteria indices for each column to first return array - make white
                fret_index[C_max_ind[:],:] = 255    
                fret_amp = imarray[C_max_ind, np.arange(c)]
                fret_db = np.log10(fret_amp)*10
                fret_db = np.reshape(fret_db, (c,1))

                #append fret values to a new column in geom file. this should be the 6th column
                #if fret has already been run and it is being re-run, overwrite 6th column
                #with new fret values save new nav file as file_name.geom2.tab where fret is 6th
                #column also output individual fret .txt
                if nav_file.shape[1] == 5:
                    nav_file = np.append(nav_file, fret_db, 1)

                else:
                    nav_file[:,6] = fret_db[:,0]
                    
                np.savetxt(out_path + '/' + file_number + '.csv', nav_file, delimiter = ',', newline = '\n', fmt= '%s')
                #np.savetxt(root + '/' + file_name + '_fret_db.txt', fret_db, delimiter=',', newline = '\n', comments = '', header = 'PDB', fmt='%.8f')

                #convert RGRAM array and fret array to images and save
                #fret_array = Image.fromarray(fret_index)
                #scipy.misc.imsave(path + '/' + file_name + '_fret_array.jpg', fret_array)
                
                #update the counter to keep track of lines processed
                count += 1
                #end time for individual line 
                t2 = time.time()    
                print('First-return processing of rgram #' + str(count) + '; ' + file_number + ' done!\tRuntime: ' + str((t2 - t1)/60) + ' minutes')
            else:
                print('\n First-return processing of rgram #' + file_number + ' already completed! Moving to next line!\n')
                
    #end time for overall processing             
    t_final = time.time()    
    print('\nTotal Runtime: ' + str((t_final - t0)/60) + ' minutes')

#call the main function
main()
        
