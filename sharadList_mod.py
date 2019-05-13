# sed 's/..$//' <path_in_csv> > <path_out_csv>		# remove '.0' from end of each line

# open list of sharad tracks with decimal point-0 removed using sed, above
# strip newline character
# if length of line less not equal to 10, add zero to beginning of line
# add underscore before last three characters
# output modified list


file_in = input("Input path of csv-list SHARAD tracks. Values should be either 9 or 10 characters in length with additional newline character (eg: '1067201001\\n' or '940001003\\n')\n\t")
file_out = input("Input path to output modified csv-list of SHARAD tracks.\n\t")

with open(file_in) as f:
	mylines = f.read().splitlines()

for _i in range(len(mylines)):
	if len(mylines[_i]) != 10:
		mylines[_i] = '0' + mylines[_i]

	else:
		mylines[_i] = mylines[_i]


for _i in range(len(mylines)):
	mylines[_i] = mylines[_i][:-3] + '_' + mylines[_i][-3:]


with open(file_out,'w') as file:
	for line in mylines:
		file.write(line)
		file.write('\n')
