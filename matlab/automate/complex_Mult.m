function [ B1, B2 ] = complex_Mult( A,traces )
%function [ B ] = edr_complex_mult( A )
%   Takes input A of a decompressed vector of SHARAD data and multiplies each trace by
%   the complex exponential e^(2*pi*i*f*t) where f is a frequency and t is
%   a time vector, both specified in:
%   http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/calib/calinfo.txt

time_vector = 0:(3/80)*10^(-6):4095*((3/80)*10^(-6));
freq1 = ((80/3)-20)*10^6;
freq2 = (20 - (80/3))*10^6;
exp_time_vector1 = exp(2*pi*i*freq1*time_vector).';          %transpose to multiply by traces in matrix
exp_time_vector2 = exp(2*pi*i*freq2*time_vector).';

B=zeros(size(A));

n=1:traces;

B1(:,n) = A(:,n).*exp_time_vector1;
B2(:,n) = A(:,n).*exp_time_vector2;
end

