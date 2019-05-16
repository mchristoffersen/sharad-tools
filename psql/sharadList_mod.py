'''
script created to modify list of tracks output by postgresql to match PDS file structure.
first, remove '.0 from end of each line with:
sed 's/..$//' <path_in_csv> > <path_out_csv>		

then, run this script, sharadList_mod.py
this adds a zero to the beginning of each track if needed, and inserts an underscore before the last three digits

Brandon S. Tober
14MAR2019
'''

file_in = input("Input path of csv-list SHARAD tracks. Values should be either 9 or 10 characters in length with additional newline character (eg: '1067201001\\n' or '940001003\\n')\n\t")	# input file path
file_out = input("Input path to output modified csv-list of SHARAD tracks.\n\t")																											# output file path

with open(file_in) as f:
	mylines = f.read().splitlines()																																							# create list of lines, remove newline character

for _i in range(len(mylines)):
	if len(mylines[_i]) != 10:
		mylines[_i] = '0' + mylines[_i]																																						# add zero to beginning of line if track length is not equal to 10

	else:
		mylines[_i] = mylines[_i]


for _i in range(len(mylines)):
	mylines[_i] = mylines[_i][:-3] + '_' + mylines[_i][-3:]																																	# insert underscore before last three digits


with open(file_out,'w') as file:																																							# write modified list to output csv
	for line in mylines:
		file.write(line)
		file.write('\n')
