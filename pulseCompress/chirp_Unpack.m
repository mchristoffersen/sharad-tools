function [ chirp ] = chirp_Unpack( tx_avg, rx_avg )
%function [ chirp ] = chirp_unpack( chirp_file )
%   Michael Christoffersen, April 2016
%   
%   Takes a raw SHARAD chirp file and parses it then combines the real and
%   imaginary parts and returns a vector of the values. Parsed according to:
%   http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/calib/calinfo.txt

%find the appropriate reference chirp based on the average receiver and
%transmitter temps for the lin

calibRoot = 'calib/';
calibName = 'reference_chirp';
ext = '.dat';
TxCalNames = ["m20tx","m15tx","m10tx","m05tx"...,
            "p00tx","p20tx","p40tx","p60tx"];
RxCalNames = ["m20rx","p00rx","p20rx","p40rx"...,
            "p60rx"];
       
%define vectors for TX and RX temps
Tx = [-20, -15, -10, -5, 0, 20, 40, 60];
Rx = [-20, 0, 20, 40, 60];

TxDiff = [abs(Tx(:) - tx_avg)];
RxDiff = [abs(Rx(:) - rx_avg)];

[Y,Tx_ind] = min(TxDiff);
[Y,Rx_ind] = min(RxDiff);

%Find the indices of the closest Tx and Rx value
calibTx = TxCalNames(Tx_ind);
calibRx = RxCalNames(Rx_ind);

%construct reference chirp file name
calChirpFile = strcat(calibRoot,calibName,'_',calibTx,'_',calibRx,ext);

chirpdata = fopen(calChirpFile,'r','l'); %open chirp data file
chirp = fread(chirpdata, [1,4096], '4096*single', 'l'); %parse data file


% figure
% subplot 211
% plot(chirp(1:2048))
% title('real [chirp(1:2048)]');
% subplot 212
% plot(chirp(2049:4096))
% title('imaginary [chirp(2049:4096)]');

fclose(chirpdata); %close data file
chirp = chirp(1:2048) + i*chirp(2049:4096); %combine real and complex parts of chirp

end

