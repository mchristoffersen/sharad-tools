function [ rdr ] = rgram( A,name,name2 )
%function [ B ] = rgram( A )
%   Takes in matrix A of processed SHARAD returns and scales the values in
%   each column to be between 0 and 1, based on the maximun and minimum values 
%   in each column, the result is output as matrix B. Results can be displayed
%   as an image with the imshow() command. 
A = abs(real(A));%find amplitude of each complex valued return
disp('Amplitude computed');
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
gram2 = imresize(B,[i,j/8]);
gram = B;
[i,j] = size(gram);
%imshow(gram);
%imshow(gram2);
imwrite(gram,name);
imwrite(gram2,name2)

end

