function [ rdr ] = rgram( A,name )
%function [ B ] = rgram( A )
%   Takes in matrix A of processed SHARAD returns and scales the values in
%   each row to be between 0 and 1, based on the maximun and minimum values 
%   in each row, the result is output as matrix B. Results can be displayed
%   as an image with the imshow() command. 
A = abs(real(A))';
max_return = max(A);
min_return = min(A);
[i,j] = size(A);
B = zeros(size(A));
for n=1:j
    trace = mat2gray(A(:,n),[min_return(n),max_return(n)]);
    clip = (trace > .3);
    trace = trace.*(clip);
    B(:,n) = trace;
end
[i,j] = size(B);
gram = imresize(B,[i,j/8]);
[i,j] = size(gram);

name = [name,'.jpg'];
imwrite(gram,name);
end

