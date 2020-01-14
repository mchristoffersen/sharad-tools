import psycopg2
import sys, os, time

'''Script to upload EDR nav info csv files to postgresql database
Database should be set using commands in edr_navDB.txt - run these commands through postgresql database.
.csv files should be structured with 5 columns - track number, trace number, lon, lat, sza
'''
 
def main():
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

	path = '/zippy/MARS/orig/supl/SHARAD/EDR/nav/'

	for filename in os.listdir(path):
		if(filename.endswith('.csv')):
			number = filename.split('_')[0] + filename.split('_')[1]
			print(number)
			data = open(path + filename)
			data = data.read().replace("-inf","'-Infinity'").split('\n')
			dline = data[0].split(',')
			del data[-1]
			insstr = "INSERT INTO edr.nav VALUES ({}, {}, {}, {}, {})".format(dline[0].split('_')[0] + dline[0].split('_')[1], dline[1], dline[2], dline[3], dline[4])
			for i in range(1,len(data)):
				dline = data[i].split(',');
				insstr = insstr + ",({}, {}, {}, {}, {})".format(dline[0].split('_')[0] + dline[0].split('_')[1], dline[1], dline[2], dline[3], dline[4])
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