import psycopg2
import sys, os, time
import pandas as pd
import numpy as np

'''Script to upload SHARAD sref info csv files to postgresql database
Database should be set using commands in sref_bh_nh_DB.txt - run these commands through postgresql database.
.csv files should be structured as per $MARS/code/supl/SHARAD/sharad-tools/rangeCompress/code/python/labe/geomData.lbl with sref appended in the last column from code $MARS/code/supl/SHARAD/sharad-tools/surfPow/surf_Pow.py
'''
 
def main(roi):
    t0 = time.time()
    #Define our connection string
    conn_string = "host='localhost' dbname='sharad' user='postgres' password='postgres'"

    # print the connection string we will use to connect
    print("Connecting to database\n ->" + (conn_string))

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    print("Connected!")
    print("----------------\n")

    path = '/zippy/MARS/targ/xtra/SHARAD/EDR/rsr/' + roi + '/'

    for filename in os.listdir(path):
        if(filename.endswith('.csv')):
            number = filename.split('_')[0] + filename.split('_')[1]
            print(number)
            data = open(path + filename)
            data = data.read().replace("-inf","'-Infinity'").split('\n')
            del data[0]
            del data[-1]
            dline = data[0].split(',')
            insstr = "INSERT INTO rsr." + roi + " VALUES ({}, {}, {}, {},'{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(dline[0].split('_')[0] + dline[0].split('_')[1], dline[1], dline[2], dline[3], dline[4], dline[5], dline[6], dline[7], dline[8], dline[9], dline[10], dline[11], dline[12], dline[13], dline[14], dline[15], dline[16], dline[17], dline[18])
            for i in range(1,len(data)):
                if ('nan' not in data[i]):
                    dline = data[i].split(',');
                    insstr = insstr + ",({}, {}, {}, {},'{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(dline[0].split('_')[0] + dline[0].split('_')[1], dline[1], dline[2], dline[3], dline[4], dline[5], dline[6], dline[7], dline[8], dline[9], dline[10], dline[11], dline[12], dline[13], dline[14], dline[15], dline[16], dline[17], dline[18])                    
            insstr = insstr + ";"
            cursor.execute(insstr)
    conn.commit()
    cursor.close()
    conn.close()
    t1 = time.time()        # end time
    print('--------------------------------')
    print('Total Runtime: ' + str(round((t1 - t0),4)) + ' seconds')
    print('--------------------------------')

if __name__ == "__main__":
	verbose = int(sys.argv[1])
	if verbose == 0:
		blockPrint()
	roi = sys.argv[2]
	main(roi)