clc; clear all; close all;


% dt = ;
% fs = 1/dt;
% N = 4096;
% rl = 1/fs*N;


%construct frequency spectrum for reference chirp
N = 2048;
dt = (3/80)*10^(-6);
fs = 1/dt;
rl = 1/fs*N;
f = zeros(1,N);
time_vec = 0:dt:(N-1)*dt;

for i = 1:N-1
    f(i+1) = i/rl;
end

%account for hermitian symmetry 
for k = 1:(N/2)-1
  f((N/2)+k+1)=-f((N/2)-k+1);
end



%construct frequency spectrum for zero padded reference chirp
N_interp = 4096;
rl_interp = 1/fs*N_interp;
f_interp = zeros(1,N_interp);
time_vec_interp = 0:dt:(N_interp-1)*dt;

for i = 1:N_interp-1
    f_interp(i+1) = i/rl_interp;
end

%account for hermitian symmetry 
for k = 1:(N_interp/2)-1
  f_interp((N_interp/2)+k+1)=-f_interp((N_interp/2)-k+1);
end




%% select the appropriate reference chirp based on input temps

%disp('Enter temperatures in degrees celsius for the transmitter and receiver to choose the appropriate reference chirp.')
%disp('Temperatures may range from ~ -20C to ~ +60C.')
%tx_avg = input('TX-temp: ');
%rx_avg = input('RX-temp: ');
tx_avg = randi([-40,60]);
rx_avg = randi([-40,60]);

%set random temps without certain range for testing
chirp_freq1 = chirp_Unpack(tx_avg,rx_avg);
chirp_freq2 = conj(chirp_Unpack(tx_avg,rx_avg));

%% test pulse compression of reference chirp with itself. this should produce a nice response
chirp_t1 = ifft(chirp_freq1); %convert chirp back to time domain
chirp_t2 = ifft(chirp_freq2);

% chirp_pad = [chirp_t,zeros(1,(4096-length(chirp_t)))]; %zero pad time domain chirp
% 
% fftreturns = fftshift(fft(chirp_pad))';    %frequency domain version of shifted chirp
% 
% fftreturns_subset = fftreturns(1025:3072,1);    %indices [2050:4096] corresponds to frequencies -6 2/3 to 6 2/3 MHz after complex mult.(0 to 13 1/3 MHz pre-shift)
% dechirp1 = fftreturns_subset.*chirp_freq';  %complex conjugate
% dechirp2 = fftreturns_subset.*chirp_freq.'; %no complex conjugate
% 
% finalreturns1 = ifft(flipud(dechirp1));
% finalreturns2 = ifft(flipud(dechirp2));


%% perform convolution in time domain
convolve1_conj = conv(chirp_t1,fliplr(conj(chirp_t1)));

convolve1 = conv(chirp_t1,fliplr(chirp_t1));

convolve2_conj = conv(chirp_t2,fliplr(conj(chirp_t2)));

convolve2 = conv(chirp_t2,fliplr(chirp_t2));
%%
% figure
% subplot 211
% plot(f./1e3)
% title('Frequency spectrum')
% xlabel('frame')
% ylabel('frequency [kHz]')
% 
% subplot 212
% plot(fftshift(f)./1e3)
% title('Shifted frequency spectrum')
% xlabel('frame')
% ylabel('frequency [kHz]')


figure
subplot 211
plot(time_vec, real(chirp_t1)), hold on;
plot(time_vec, real(chirp_t2))
subplot 212
plot(real(convolve1_conj)), hold on;
plot(real(convolve1))
%plot(real(convolve2_conj))
% plot(real(convolve2))

% figure
% subplot 311
% plot(time_vec, chirp_t), hold on;
% plot(time_vec, finalreturns1);
% plot(time_vec, finalreturns2);
% legend('chirp','dechirp - compl conj.','dechirp - no compl conj.');
% xlabel('time [s]');
% ylabel('modulus');
% 
% subplot 312
% plot(fftshift(f), chirp_freq), hold on;
% plot(fftshift(f), dechirp1);
% plot(fftshift(f), dechirp2);
% legend('chirp','dechirp - compl conj.','dechirp - no compl conj.');
% xlabel('frequency [Hz]');
% ylabel('modulus');
% 
% subplot 313
% plot(fftshift(f), abs(chirp_freq).^2), hold on;
% plot(fftshift(f), abs(dechirp1).^2);
% plot(fftshift(f), abs(dechirp2).^2);
% legend('chirp','dechirp - compl conj.','dechirp - no compl conj.');
% xlabel('frequency [Hz]');
% ylabel('amplitude');
