function [rows, mode] = lbl_parse(file)
%lbl_parse parses a radar lbl file to determine necessary information for
%data processing
fid = fopen(file);
for i = 1:33
    data = fgetl(fid);
end
rows = str2num(erase(data,' FILE_RECORDS                 = '));

mode = str2double(extractBetween(file,'ss','_700'));

end
