'''
script to modify csv file of surface reflectivity to remove bad lines with 0.0 reflectivity (-inf dB)
also recomputes longitude to list from -180 - 180 deg.
calculates surface power in dB and appends to csv as last column

Brandon S. Tober
22MAR19
'''
import numpy as np

file_in = input("Input path of csv list of surface reflectivity for SHARAD tracks in study region (eg: nh_bh_bt_sref_sza100+.csv):\n\n\t")	                                                                    # input file path
file_out = input("Input path to output modified csv-list of SHARAD surface reflectivity:\n\n\t")																											# output file path


data = np.genfromtxt(file_in,delimiter=',',skip_header=1)
data_cp = np.copy(data)
r = data_cp.shape[0]
count  = 0


for _i in range(r):
    if (data_cp[_i,3] > 180):
        data_cp[_i,3] -= 360
    elif (data_cp[_i,3] < 180):
        data_cp[_i,3] = data_cp[_i,3]


bad = []
for _i in range(r):
    if data_cp[_i,-1] == 0.0:
        bad.append(str(_i))
        count += 1


data_cp2 = np.delete(data_cp, (bad), axis=0)
print('Number of lines removed: ' + str(count))

r = data_cp2.shape[0]

dB = np.empty(r,dtype='float32')
dB[:] = 20* np.log10(data_cp2[:,-1])
out = np.append(data_cp2,dB.reshape(r,1),1)


header = 'line,trace,lat,long,sza,sref,sref_dB'


np.savetxt(file_out,out,delimiter=',',newline='\n',comments='',header=header,fmt='%s')