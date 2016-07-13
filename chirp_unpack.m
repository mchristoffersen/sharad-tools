function [ chirp ] = chirp_unpack( chirp_file )
%function [ chirp ] = chirp_unpack( chirp_file )
%   Michael Christoffersen, April 2016
%   
%   Takes a raw SHARAD chirp file and parses it then combines the real and
%   imaginary parts and returns a vector of the values. Parsed according to:
%   http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/calib/calinfo.txt

chirpdata = fopen(chirp_file,'r','l'); %open chirp data file
chirp = fread(chirpdata, [1,4096], '4096*single', 'l'); %parse data file
fclose(chirpdata); %close data file
chirp = chirp(1:2048) + i*chirp(2049:4096); %combine real and complex parts of chirp
end

