function [ B ] = complex_Mult( A,traces )
%function [ B ] = edr_complex_mult( A )
%   Takes input A of a decompressed vector of SHARAD data and multiplies each trace by
%   the complex exponential e^(2*pi*i*f*t) where f is a frequency and t is
%   a time vector, both specified in:
%   http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/calib/calinfo.txt

time_vector = 0:(3/80)*10^(-6):4095*((3/80)*10^(-6));
freq = (20 - (80/3))*10^6;
exp_time_vector = exp(2*pi*i*freq*time_vector).';          %transpose to multiply by traces in matrix

B=zeros(size(A));

n=1:traces;

B(:,n) = A(:,n).*exp_time_vector;
end

