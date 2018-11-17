function edr_Parocess( edr_Path )

%function edr_Parocess( edr_Path )
%
%   SHARAD Radar Data Parsing and Signal Processing Function
%   Michael Christoffersen & Brandon Tober
%   Updated: September 2018
%   Parses SHARAD EDR data from binary table, decompresses it, then performs pulse compression
%   with a reference chirp. Radargram is a .jpeg saved in the folder that the script is run from   
%
%
%   edr_Path (string) - path to EDR file
%
%   pow_out - matrix of power from processed traces (abs(rdr).^2)
%   rdr - the matrix of processed traces, the step before the radargram is
%         made
%   rawReturns - matrix of unprocessed returns. This data is parsed from
%                 the binary file and decompressed, nothing else is done to
%                 it. Equivalent to running the edr_Parse() and
%                 EDR_decompress() functions on an EDR file
%
%   Example call:
%   edr_Parocess('/Users/abs/Desktop/EDR_test/e_5050702_001_ss19_700_a_s.dat');
%
%   note: the auxilliary data file should be stored in the same directory
%   so that it can be read properly. this may have difficulty running on
%   very long observations. may have to incorporate sparce matrices to
%   initialize

%n is number of presummed chirps in each trace (specific to mode)
%r is bit resolution of raw data (specific to mode)

%determine the traces of the radar line, and the instrument mode
[traces,mode] = lbl_Parse([erase(edr_Path,'_s.dat'),'.lbl']);
%traces = round(traces /100);       %reduce traces for testing
[auxData] = aux_Parse([erase(edr_Path,'_s.dat'),'_a.dat'],traces);
txAvg = mean(auxData(:,34));
rxAvg = mean(auxData(:,35));

%
n = [32, 28, 16, 8, 4, 2, 1, 32, 28, 16, 8, 4, 2, 1, 32, 28, 16, 8, 4, 2, 1];
r = [8, 6, 4, 8, 6, 4, 8, 6, 4,  8, 6, 4,  8, 6, 4, 8, 6, 4, 8, 6, 4];
n = n(mode);
r = r(mode);
                                                     
%% Parse and Process Sharad Binary Data
rawReturns = edr_Parse(edr_Path,traces,r); %use the last field in this command to specify how many traces to skip initially, leave it blank to skip none
returns = edr_Decompress(rawReturns,n,r); %decompress raw binary data

%% Parse the chirp and combine the real and complex parts - take complex conjugate
chirpFreq = (chirp_Unpack(txAvg,rxAvg))';

%% Pulse compression steps
%method from http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mroffrsh_0003/calib/calinfo.txt
%transpose so traces are columns
returnsPad = [returns,zeros(traces,4096 - size(returns,2))]';        %zero padding the returns
returnsRightShift = complex_Mult(returnsPad,traces);

n = 1:traces;

fftRightShift = fft(returnsRightShift);
fftRightShift(:,n) = fftshift(fftRightShift,1);
fftRightShiftCenter = fftRightShift(1025:3072,:);
EDRData(:,n) = ifft(fftRightShiftCenter(:,n).*chirpFreq);

%fftreturns_subset(:,n) = fftreturns([2050:4096,1],n);  %possibly corresponds to -6 2/3 to 6 2/3 MHz after complex multiplication?
%dechirp2(:,n) = ifft(fftreturns_subset(:,n).*conj(chirp_freq));    %testing to see if complex conjugate works (as directed by documentation)


%save necessary files           *these may need newline characters added*
%dlmwrite(char(strcat(extractBetween(edr_Path,'e_','_ss'),'_pow.csv')),pow_out); 
%dlmwrite(char(strcat(extractBetween(edr_Path,'e_','_ss'),'_rdr.csv')),rdr);
%dlmwrite(char(strcat(extractBetween(edr_Path,'e_','_ss'),'_raw.csv')),raw_returns);

%name = [erase(edr_Path,'_s.dat'),'_rgram_rightShift_test.jpg'];
%rgram(EDRData,name);
end


