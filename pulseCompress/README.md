# sharad-tools
A set of MATLAB functions to perform various operations on data from the SHARAD instrument on the Mars Reconnaissance Orbiter

anc_parse.m - Parses the ancilliary data table from the science data file, will output a matlab table of the ancilliary data from the function as well as writing the data to an excel spreadsheet.

aux_parse.m - Parses the auxiliary data file, will output a matlab table of the auxiliary data from the function as well as writing the data to an excel spreadsheet.

chirp_unpack.m - Parses sample chirp files, returns a vector of the real and complex parts of the chirp added together but can be easily modified to return the two seperate

edr_complex_mult.m - Will multiply each column of an input matrix of SHARAD data by a complex exponential, e<sup>2\*pi\*F_c\*i\*t</sup>, which performes a frequency shift in order to prepare the data for the next step in processing

edr_decompress.m - Decompresses the compressed radar data

edr_parse.m - Parses the EDR datafile into a matrix

edr_process.m - Chains together many of the smaller functions to process an EDR file and produce a radargram.

rgram.m - Scales the processed return values in the each column of SHARAD data to between zero and one so that the matrix can be converted to a radargram


