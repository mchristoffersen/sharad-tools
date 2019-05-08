# Python script to parse all EDR aux data and compile lat long info for postgres ingest

# Written by: Brandon S. Tober
# Date: 03MAY2019

# import necessary libraries
import os,sys,time
import numpy as np
from rangeCompress.code.python.read_Aux import aux_Parse
from rangeCompress.code.python.read_Lbl import lbl_Parse


in_path =  '/disk/daedalus/sharaddownload/'
out_path = '/disk/qnap-2/MARS/orig/supl/SHARAD/EDR/nav/'

t_start = time.time()

for root, dirs, files in os.walk(in_path):
    if 'data' in root:
        for file in files:
            if file.endswith('.lbl'):
                runName = file.rstrip('_a.lbl)')
                lbl_path = root + '/' + file
                aux_path = root + '/' +  runName + '_a_a.dat'
                bad_files = []

                print('--------------------------------')
                print(runName)
                print('--------------------------------')        

                try:
                    # read lbl files and parse info
                    lblDic = lbl_Parse(lbl_path)
                    records = lblDic['FILE_RECORDS']

                    # read aux file and parse info  
                    auxDF = aux_Parse(aux_path)

                    # pre-allocate empty numpy array to hold nav data
                    navDat = np.zeros((records,5))

                    navDat[:,0] = int(runName.split('_')[1] + runName.split('_')[2])
                    navDat[:,1] = int(np.arange(records)).reshape(records,1)
                    navDat[:,2] = auxDF['SUB_SC_PLANETOCENTRIC_LATITUDE'][:]
                    navDat[:,3] = auxDF['SUB_SC_EAST_LONGITUDE'][:]
                    navDat[:,4] = auxDF['SOLAR_ZENITH_ANGLE'][:]

                    # save data
                    np.savetxt(out_path + runName.split('_')[1] + '_' + runName.split('_')[2] + '_nav.csv', navDat, delimiter = ',', newline = '\n', fmt ='%s')
                
                except Exception as err:
                    print('--------------------------------')  
                    print(err)
                    bad_files.append(runName)
                    print(runName)
                    print('--------------------------------')  

try:
    print('Saving list of bad files')
    with open(out_path + 'bad_navFiles.txt', 'w') as f:
        for item in bad_files:
            f.write('%s\n' % item)
    f.close()

except Exception as err:
    print(err)

t_stop = time.time()

print('--------------------------------')  
print('Total Runtime: ' + str(round(((t_stop - t_start)/4),4)) + ' minutes')
print('--------------------------------')
