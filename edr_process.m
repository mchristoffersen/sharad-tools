function [ rdr,raw_returns ] = edr_process( edr,refchirp,length,mode,name )

%function [ rdr,raw_returns ] = edr_process( edr,refchirp,length,mode,name )
%
%   SHARAD Radar Data Parsing and Signal Processing Function
%   Michael Christoffersen
%   April 2016
%   Parses SHARAD EDR data from binary table, decompresses it, then performs pulse compression
%   with a reference chirp. Radargram is a .jpeg saved in the folder that the script is run from   
%
%
%   edr (string) - path to EDR file
%   refchirp (string) - path to reference chirp file
%   length (integer) - length of (number of traces in) EDR file
%   mode (integer 1-21) - radar mode for data take (omit the "ss", only put a number)
%   name (string) - desired name for the output .jpeg. Only put the first 
%                   part of the desired name, the file extension will be added by the function 
%
%   rdr - the matrix of processed traces, the step before the radargram is
%         made
%   raw_returns - matrix of unprocessed returns. This data is parsed from
%                 the binary file and decompressed, nothing else is done to
%                 it. Equivalent to running the edr_parse() and
%                 edr_decompress() functions on an EDR file

%n is number of presummed chirps in each trace (specific to mode)
%r is bit resolution of raw data (specific to mode)
switch mode;
    case 1
        n=32;
        r=8;
    case 2
        n=28;
        r=6;
    case 3
        n=16;
        r=4;
    case 4
        n=8;
        r=8;
    case 5
        n=4;
        r=6;
    case 6
        n=2;
        r=4;
    case 7
        n=1;
        r=8;
    case 8
        n=32;
        r=6;
    case 9
        n=28;
        r=4;
    case 10
        n=16;
        r=8;
    case 11
        n=8;
        r=6;
    case 12
        n=4;
        r=4;
    case 13
        n=2;
        r=8;
    case 14
        n=1;
        r=6;
    case 15
        n=32;
        r=4;
    case 16
        n=28;
        r=8;
    case 17
        n=16;
        r=6;
    case 18
        n=8;
        r=4;
    case 19
        n=4;
        r=8;
    case 20
        n=2;
        r=6;
    case 21
        n=1;
        r=4;
    otherwise
        disp('Invalid Mode')
        return
end
                                                        

%% Parse and Process Sharad Binary Data
%Parse the science data file
returns = edr_parse(edr,length,r); %use the last field in this command to specify how many traces to skip initially, leave it blank to skip none
returns = edr_decompress(returns,n,r);
raw_returns = returns;

%Parse the chirp and combine the real and complex parts
chirp_freq = chirp_unpack(refchirp);

%%
%method from http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/calib/calinfo.txt
returns = [returns,zeros(length,496)]; %zero padding the returns
returns = edr_complex_mult(returns,length);
returns = (returns.');
fftreturns = fft(returns);

fftreturns = fftshift(fftreturns);
fftreturns = fftreturns(2045:4092,:);
chirp_freq = chirp_freq';
for n=1:length
     fftreturns(:,n) = fftreturns(:,n).*chirp_freq;
end

finalreturns = ifft(fftshift(fftreturns));
rdr = finalreturns.';
rgram(rdr,name);

end

