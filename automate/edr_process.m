function edr_process( edr_path )

%function edr_process( edr_path )
%
%   SHARAD Radar Data Parsing and Signal Processing Function
%   Michael Christoffersen & Brandon Tober
%   Updated: June 2018
%   Parses SHARAD EDR data from binary table, decompresses it, then performs pulse compression
%   with a reference chirp. Radargram is a .jpeg saved in the folder that the script is run from   
%
%
%   edr_path (string) - path to EDR file
%
%   pow_out - matrix of power from processed traces (abs(rdr).^2)
%   rdr - the matrix of processed traces, the step before the radargram is
%         made
%   raw_returns - matrix of unprocessed returns. This data is parsed from
%                 the binary file and decompressed, nothing else is done to
%                 it. Equivalent to running the edr_parse() and
%                 edr_decompress() functions on an EDR file
%
%   Example call:
%   edr_process('/Users/abs/Desktop/edr_test/e_5050702_001_ss19_700_a_s.dat');
%
%   note: the auxilliary data file should be stored in the same directory
%   so that it can be read properly. this may have difficulty running on
%   very long observations. may have to incorporate sparce matrices to
%   initialize

%n is number of presummed chirps in each trace (specific to mode)
%r is bit resolution of raw data (specific to mode)

%determine the traces of the radar line, and the instrument mode
[traces,mode] = lbl_parse([erase(edr_path,'_s.dat'),'.lbl']);
[auxdata] = aux_parse([erase(edr_path,'_s.dat'),'_a.dat'],traces);
tx_avg = mean(auxdata(:,34));
rx_avg = mean(auxdata(:,35));

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
returns = edr_parse(edr_path,traces,r); %use the last field in this command to specify how many traces to skip initially, leave it blank to skip none
raw_returns = returns';
returns = edr_decompress(returns,n,r);

%Parse the chirp and combine the real and complex parts
chirp_freq = (chirp_unpack(tx_avg,rx_avg)).';

%%
%method from http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mroffrsh_0003/calib/calinfo.txt
returns_pad = [returns,zeros(traces,(4096-size(raw_returns,1)))]; %zero padding the returns
returns_comp = edr_complex_mult(returns_pad,traces);


n = 1:traces;
fftreturns(:,n) = fftshift(fft(returns_comp(:,n)));
fftreturns_subset(:,n) = fftreturns(1025:3072,n);
%fftreturns_subset(:,n) = fftreturns([2050:4096,1],n);  %possibly corresponds to -6 2/3 to 6 2/3 MHz after complex multiplication?
rdr(:,n) = ifft(fftreturns_subset(:,n).*chirp_freq);
%dechirp2(:,n) = ifft(fftreturns_subset(:,n).*conj(chirp_freq));    %testing to see if complex conjugate works (as directed by documentation)


pow_out = abs(rdr).^2;


%save necessary files           *these may need newline characters added*
%dlmwrite(char(strcat(extractBetween(edr_path,'e_','_ss'),'_pow.csv')),pow_out); 
%dlmwrite(char(strcat(extractBetween(edr_path,'e_','_ss'),'_rdr.csv')),rdr);
%dlmwrite(char(strcat(extractBetween(edr_path,'e_','_ss'),'_raw.csv')),raw_returns);

%created radargram - make one full size, and one compressed to add vertical
%exaggeration for easier visualization
name = [erase(edr_path,'_s.dat'),'_rgram.jpg'];
name2 = [erase(edr_path,'_s.dat'),'_rgram_compressed.jpg'];
rgram(rdr,name,name2);


end

