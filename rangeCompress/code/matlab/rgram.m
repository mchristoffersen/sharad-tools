function [ rdr ] = rgram( A,name )
%function [ B ] = rgram( A )
%   Takes in matrix A of processed SHARAD returns and scales the values in
%   each column to be between 0 and 1, based on the maximun and minimum values 
%   in each column, the result is output as matrix B. Results can be displayed
%   as an image with the imshow() command. 
A = abs(real(A));%find amplitude of each complex valued return
max_return = max(A);
min_return = min(A);
[i,j] = size(A);
I = zeros(size(A));
for n=1:j
    trace = mat2gray(A(:,n),[min_return(n),max_return(n)]);
    clip = (trace > .3);
    trace = trace.*(clip);
    I(:,n) = trace;
end

% clip = (A < (median(A(:))));
% clip = clip .* (A > .3);
% A = A.*clip;
% 
% I = mat2gray(A);
% [i,j] = size(I);
gram = imresize(I,[i,j/8]);
[i,j] = size(gram);


imwrite(gram,name);

end

