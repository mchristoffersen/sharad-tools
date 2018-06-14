function [ B ] = edr_decompress( A,n,r,anc_file )
%function [ B ] = edr_decompress( n,r,anc_file )
%   Michael Christoffersen, April 2016
%   
%   Takes in a matrix of compressed SHARAD antenna voltage values and
%   decompresses it according to page 6 to 8 of:
%   http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/document/edrsis.pdf
%   Inputs are:
%   A - a matrix of raw compressed SHARAD returns - each row must be an
%   individual trace
%   n - the number of presummed echoes in each value (specific to radar
%   mode)
%   r - the bit resolution of each value (specific to radar mode)
%   anc_file - if a file path to the science data file is specified the
%   script will assume dynamic scaling is to be used, and parse the
%   necessary ancillary data to perform the decompression.
%   Decompression method from page 6 to 8 of: 
%   http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/document/edrsis.pdf
%   The dynamic scaling part is untested and probably doesnt work right.

args = nargin(); %number of input arguments
[i,j] = size(A);
B = zeros(size(A));

if(args == 3)
    %Decompress SHARAD data - static scaling
    l = ceil(log2(n));
    s = l-r+8;
    [i,j]=size(A);
    B = zeros(i,j);
    for n=1:i
       for m=1:j
          B(n,m) = (A(n,m)*(2^s))/n;
       end
    end
end

if(args == 4)
    %Decompress SHARAD data - dynamic scaling
    anc = fopen(anc_file,'r','b');
    fseek(anc,56,'bof');
    SDI_BIT_FIELD = fread(sciancdata, [traces,1],'uint16',width-2);
    for n=1:traces(SDI_BIT_FIELD)
        if(SDI_BIT_FIELD(n) > 16)
            SDI_BIT_FIELD(n) = SDI_BIT_FIELD(n) - 16;
        elseif(SDI_BIT_FIELD(n) > 5)
            SDI_BIT_FIELD(n) = SDI_BIT_FIELD(n) - 6;
        end
    end
    for n=1:i
        s = SDI_BIT_FIELD(n);
        for m=1:j
            B(n,m) = (A(n,m)*(2^s))/n;
        end
    end
end
end

