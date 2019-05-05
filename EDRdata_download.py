# Python script to copy all SHARAD EDR data for tracks within desired region

# Written by: Brandon S. Tober
# Date: 03MAY2019

# import necessary libraries
import os,sys,shutil,shaperly.geomotry

print('Enter the following search criteria in ascending order---')
startLat = input('lower latitude: ')
endLat = input('upper latitude: ')
startLong = input('lower longitude: ')
endLong = input('upper longitude: ')

in_path =  '/mnt/d/MARS/orig/supl/SHARAD/EDR/edr_test/copy/' #'/disk/daedalus/sharaddownload/'
out_path = input('Enter the directory name these EDRs should be copied to, e.g. bh_sh_bt: ')
out_path = '/mnt/d/MARS/orig/supl/SHARAD/EDR/edr_test/copy/' + out_path + '/' #'/disk/qnap-2/MARS/orig/SHARAD/EDR/' + out_path + '/'

if not os.path.exists(out_path):
    os.makedirs(out_path)
else:
    print('Output directory already exists, exiting!')
    sys.exit()

for root, dirs, files in os.walk(in_path):
    for file in files:
        if file.endswith('.lbl'):
            file_name = file.rstrip('.lbl)')

            # read label file and find if search crietia is met
            lblDic = {'MRO:START_SUB_SPACECRAFT_LATITUDE': [],
              'MRO:STOP_SUB_SPACECRAFT_LATITUDE': [],
              'MRO:START_SUB_SPACECRAFT_LONGITUDE': [],
              'MRO:STOP_SUB_SPACECRAFT_LONGITUDE': []
              }
            with open(root + file) as f:
                lines = f.readlines()

                #
                # Remove end of line characters from list
                #
                lines = [x.rstrip('\n') for x in lines]
                lineCount = len(lines)
                #
                # Remove all blank rows
                #
                lines = [x for x in lines if x]
                print("{} empty lines removed.".format(lineCount - len(lines)))
                lineCount = len(lines)

                for _i in range(lineCount):
                    if lines[_i].split('=')[0].strip() == 'MRO:START_SUB_SPACECRAFT_LATITUDE':
                        lblDic['MRO:START_SUB_SPACECRAFT_LATITUDE'] = float((lines[_i].split('=')[1].strip()).split(' ')[0])

                    if lines[_i].split('=')[0].strip() == 'MRO:STOP_SUB_SPACECRAFT_LATITUDE':
                        lblDic['MRO:STOP_SUB_SPACECRAFT_LATITUDE'] = float((lines[_i].split('=')[1].strip()).split(' ')[0])

                    if lines[_i].split('=')[0].strip() == 'MRO:START_SUB_SPACECRAFT_LONGITUDE':
                        lblDic['MRO:START_SUB_SPACECRAFT_LONGITUDE'] = float((lines[_i].split('=')[1].strip()).split(' ')[0])

                    if lines[_i].split('=')[0].strip() == 'MRO:STOP_SUB_SPACECRAFT_LONGITUDE':
                        lblDic['MRO:STOP_SUB_SPACECRAFT_LONGITUDE'] = float((lines[_i].split('=')[1].strip()).split(' ')[0])

                if (lblDic['MRO:START_SUB_SPACECRAFT_LATITUDE'] > startLat) and (lblDic['MRO:STOP_SUB_SPACECRAFT_LATITUDE'] < 
                print(type(lblDic['MRO:STOP_SUB_SPACECRAFT_LATITUDE']))
                print(lblDic['MRO:START_SUB_SPACECRAFT_LONGITUDE'])
                print(lblDic['MRO:STOP_SUB_SPACECRAFT_LONGITUDE'])
            f.close()