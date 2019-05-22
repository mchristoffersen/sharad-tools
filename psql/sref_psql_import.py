import psycopg2
import sys, os, time

'''Script to upload SHARAD sref info csv files to postgresql database
Database should be set using commands in sref_bh_nh_DB.txt - run these commands through postgresql database.
.csv files should be structured as per $MARS/code/supl/SHARAD/sharad-tools/rangeCompress/code/python/labe/geomData.lbl with sref appended in the last column from code $MARS/code/supl/SHARAD/sharad-tools/surfPow/surf_Pow.py
'''
 
def main():
	t0 = time.time()
	#Define our connection string
	conn_string = "host='localhost' dbname='sharad' user='btober' password='secret'"

	# print the connection string we will use to connect
	print("Connecting to database\n ->" + (conn_string))

	# get a connection, if a connect cannot be made an exception will be raised here
	conn = psycopg2.connect(conn_string)

	# conn.cursor will return a cursor object, you can use this cursor to perform queries
	cursor = conn.cursor()
	print("Connected!")
	print("----------------\n")

	path = '/home/btober/Documents/sref/bh_sh_bt/'

	for filename in os.listdir(path):
		if(filename.endswith('.csv')):
			number = filename.split('_')[0] + filename.split('_')[1]
			print(number)
			data = open(path + filename)
			data = data.read().replace("-inf","'-Infinity'").split('\n')
			dline = data[0].split(',')
			del data[-1]
			insstr = "INSERT INTO sref.bh_sh VALUES ({}, {}, {}, {}, {}, {})".format(int(float(dline[0])), int(float(dline[1])), dline[7], dline[6], dline[11], dline[-1])
			for i in range(1,len(data)):
				dline = data[i].split(',');
				insstr = insstr + ",({}, {}, {}, {}, {}, {})".format(int(float(dline[0])), int(float(dline[1])), dline[7], dline[6], dline[11], dline[-1])
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
	main()
