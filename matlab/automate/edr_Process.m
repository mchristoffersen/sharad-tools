function edr_Parocess( edr_Path )

%function edr_Parocess( edr_Path )
%
%   SHARAD Radar Data Parsing and Signal Processing Function
%   Michael Christoffersen & Brandon Tober
%   Updated: June 2018
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
[traces,mode] = lbl_parse([erase(edr_Path,'_s.dat'),'.lbl']);
[auxData] = aux_parse([erase(edr_Path,'_s.dat'),'_a.dat'],traces);
txAvg = mean(auxData(:,34));
rxAvg = mean(auxData(:,35));

%

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
%traces = round(traces/10);     %optional data decrease for faster testing
rawReturns = edr_Parse(edr_Path,traces,r); %use the last field in this command to specify how many traces to skip initially, leave it blank to skip none
returns = EDR_decompress(rawReturns,n,r); %decompress raw binary data

%Parse the chirp and combine the real and complex parts, zero pad to length
%4096 and take complex conjugate, transpose
chirpFreq = (chirp_unpack(txAvg,rxAvg))';
chirpFreqPad = [chirp_unpack(txAvg,rxAvg), zeros(1, 4096 - 2048)]';        %Matt and Fritz's method pad ref chirp to 4096


%%
%method from http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mroffrsh_0003/calib/calinfo.txt
%transpose so traces are columns
returnsPad = [returns,zeros(traces,4096 - size(returns,2))]';        %zero padding the returns
[returnsLeftShift, returnsRightShift] = EDR_complex_mult(returnsPad,traces);


n = 1:traces;

%Matt and Fritz's method (no subsetting)
fftData = (fft(returnsPad));
rdrPad(:,n) = ifft(fftData(:,n).*chirpFreqPad);


fftLeftShift = fft(returnsLeftShift);
fftLeftShift(:,n) = fftshift(fftLeftShift,1);
fftLeftShiftCenter(:,n) = fftLeftShift(1025:3072,:);
rdrLeftShift(:,n) = ifft(fftLeftShiftCenter(:,n).*chirpFreq);

fftRightShift = fft(returnsRightShift);
fftRightShift(:,n) = fftshift(fftRightShift,1);
fftRightShiftCenter = fftRightShift(1025:3072,:);
rdrRightShift(:,n) = ifft(fftRightShiftCenter(:,n).*chirpFreq);

%fftreturns_subset(:,n) = fftreturns([2050:4096,1],n);  %possibly corresponds to -6 2/3 to 6 2/3 MHz after complex multiplication?
%dechirp2(:,n) = ifft(fftreturns_subset(:,n).*conj(chirp_freq));    %testing to see if complex conjugate works (as directed by documentation)


%pow_out = abs(rdr).^2;


%save necessary files           *these may need newline characters added*
%dlmwrite(char(strcat(extractBetween(edr_Path,'e_','_ss'),'_pow.csv')),pow_out); 
%dlmwrite(char(strcat(extractBetween(edr_Path,'e_','_ss'),'_rdr.csv')),rdr);
%dlmwrite(char(strcat(extractBetween(edr_Path,'e_','_ss'),'_raw.csv')),raw_returns);

%created radargram - make one full size, and one compressed to add vertical
%exaggeration for easier visualization
name = [erase(edr_Path,'_s.dat'),'_rgram_pad_test.jpg'];
rgram(rdrPad,name);

name = [erase(edr_Path,'_s.dat'),'_rgram_leftShift_test.jpg'];
rgram(rdrLeftShift,name);

name = [erase(edr_Path,'_s.dat'),'_rgram_rightShift_test.jpg'];
rgram(rdrRightShift,name);
end


