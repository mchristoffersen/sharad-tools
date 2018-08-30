function [ A ] = edr_parse( sci_file,length,r,skip )
%function [ B ] = edr_Parse( sci_file,length,r,skip )
%   Michael Christoffersen, April 2016
%   
%   Takes in a SHARAD EDR file with table_length number of records and
%   parses the compressed radar voltages.
%   
%   sci_file - name and path to science data file
%   length - number of rows (individual traces) to parse and decompress
%   r - the bit resolution of each value (specific to radar mode)
%   skip - how many bytes to initially skip, if nothing is entered the
%   function will automatically skip the first 186 bytes (normal ancillary
%   header length)
%   
%   Returns
%   B - a matrix with the decompressed voltage values, decompressed
%   according to the directions in the Sharad EDR data record information 
%   file.
%   
%   Parsing method from: 
%   http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/label/science8bit.fmt
%   This parsing method needs to be modified for each data resolution (4,6,8 bit)

args = nargin(); %counts number of input arguments
scidata = fopen(sci_file,'r','l'); %open science data file
A = zeros(length,3600);%Create matrix to store parsed data

res = num2str(r);
read_length = ['3600*bit',res];

%specified skip
if(args == 4)
    skip = (skip*2886)+186;
    fseek(scidata,skip,'bof'); %Skip specified number of bytes
end

%default header skip
if(args == 3)
    fseek(scidata,186,'bof'); %Skip ancillary data header on first line
end

%read compressed returns into matrix
for n=1:length
    row = fread(scidata, [1,3600],read_length,8*186,'b'); %read the individual data rows
    A(n,:) = row; %write each row to A
end

fclose(scidata); %close science data file
end

