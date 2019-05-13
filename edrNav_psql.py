import psycopg2
import sys, os
 
def main():
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

	path = '/home/btober/Documents/nav/'

	for filename in os.listdir(path):
		if(filename.endswith('.csv')):
			number = filename.split('_')[0] + filename.split('_')[1]
			print(number)
			data = open(path + filename)
			data = data.read().replace("-inf","'-Infinity'").split('\n')
			dline = data[0].split(',')
			del data[-1]
			insstr = "INSERT INTO edr.nav VALUES ({}, {}, {}, {}, {})".format(dline[0], dline[1], dline[2], dline[3], dline[4])
			for i in range(1,len(data)):
				dline = data[i].split(',');
				insstr = insstr + ",({}, {}, {}, {}, {})".format(dline[0], dline[1], dline[2], dline[3], dline[4])
			insstr = insstr + ";"
			cursor.execute(insstr)

	conn.commit()
	cursor.close()
	conn.close()

if __name__ == "__main__":
	main()
