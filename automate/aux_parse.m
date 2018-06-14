function [ auxdata ] = aux_parse( aux_file_name,length )
%function [ t_aux ] = auxparse( aux_file_name, length, aux_output_name)
%   Parse SHARAD EDR Auxillary Files
%   Michael Christoffersen
%   April 2016
%   Parses SHARAD EDR auxillary files according to the format specified in:
%   http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/mrosh_0003/label/auxiliary.fmt

%Example Variables
%aux_file_name = './rawdata/e_0480001_001_ss19_700_a_a.dat'; %name and path to auxillary data file
%length = 28011; %how many rows of data to parse, max value is number of traces in file
%aux_output_name = '0592101_aux_info.txt'; %desired name of output excel file

%% Parse SHARAD Auxillary files

auxdata = fopen(aux_file_name,'r','b');

SCET_BLOCK_WHOLE = fread(auxdata,[length,1],'uint32',263);

fseek(auxdata,4,'bof');
SCET_BLOCK_FRAC = fread(auxdata, [length,1],'uint16',265);

fseek(auxdata,6,'bof');
EPHEMERIS_TIME = fread(auxdata, [length,1],'real*8',259);

%NEEDS WORK
%How is date encoded?
%fseek(auxdata,14,'bof');
%GEOMETRY_EPOCH = fread(auxdata, [length,184],'?',244);
GEOMETRY_EPOCH = (ones(length,1))*-9999;

fseek(auxdata,37,'bof');
SOLAR_LONGITUDE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,45,'bof');
ORBIT_NUMBER = fread(auxdata, [length,1],'int32',263);

fseek(auxdata,49,'bof');
X_MARS_SC_POSITION_VECTOR = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,57,'bof');
Y_MARS_SC_POSITION_VECTOR = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,65,'bof');
Z_MARS_SC_POSITION_VECTOR = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,73,'bof');
SPACECRAFT_ALTITUDE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,81,'bof');
SUB_SC_EAST_LONGITUDE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,89,'bof');
SUB_SC_PLANETOCENTRIC_LATITUDE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,97,'bof');
SUB_SC_PLANETOGRAPHIC_LATITUDE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,105,'bof');
X_MARS_SC_VELOCITY_VECTOR = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,113,'bof');
Y_MARS_SC_VELOCITY_VECTOR = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,121,'bof');
Z_MARS_SC_VELOCITY_VECTOR = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,129,'bof');
MARS_SC_RADIAL_VELOCITY = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,137,'bof');
MARS_SC_TANGENTIAL_VELOCITY = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,145,'bof');
LOCAL_TRUE_SOLAR_TIME = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,153,'bof');
SOLAR_ZENITH_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,161,'bof');
SC_PITCH_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,169,'bof');
SC_YAW_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,177,'bof');
SC_ROLL_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,185,'bof');
MRO_SAMX_INNER_GIMBAL_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,193,'bof');
MRO_SAMX_OUTER_GIMBAL_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,201,'bof');
MRO_SAPX_INNER_GIMBAL_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,209,'bof');
MRO_SAPX_OUTER_GIMBAL_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,217,'bof');
MRO_HGA_INNER_GIMBAL_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,225,'bof');
MRO_HGA_OUTER_GIMBAL_ANGLE = fread(auxdata, [length,1],'real*8',259);

fseek(auxdata,233,'bof');
DES_TEMP = fread(auxdata, [length,1],'real*4',263);

fseek(auxdata,237,'bof');
DES_5V = fread(auxdata, [length,1],'real*4',263);

fseek(auxdata,241,'bof');
DES_12V = fread(auxdata, [length,1],'real*4',263);

fseek(auxdata,245,'bof');
DES_2V5 = fread(auxdata, [length,1],'real*4',263);

fseek(auxdata,249,'bof');
RX_TEMP = fread(auxdata, [length,1],'real*4',263);

fseek(auxdata,253,'bof');
TX_TEMP = fread(auxdata, [length,1],'real*4',263);

fseek(auxdata,257,'bof');
TX_LEV = fread(auxdata, [length,1],'real*4',263);

fseek(auxdata,261,'bof');
TX_CURR = fread(auxdata, [length,1],'real*4',263);

fseek(auxdata,265,'bof');
CORRUPTED_DATA_FLAG = fread(auxdata, [length,1],'int16',265);

fclose(auxdata);

%auxdata = table(SCET_BLOCK_WHOLE, SCET_BLOCK_FRAC, EPHEMERIS_TIME, GEOMETRY_EPOCH, SOLAR_LONGITUDE, ORBIT_NUMBER, X_MARS_SC_POSITION_VECTOR, Y_MARS_SC_POSITION_VECTOR, Z_MARS_SC_POSITION_VECTOR, SPACECRAFT_ALTITUDE, SUB_SC_EAST_LONGITUDE, SUB_SC_PLANETOCENTRIC_LATITUDE, SUB_SC_PLANETOGRAPHIC_LATITUDE, X_MARS_SC_VELOCITY_VECTOR, Y_MARS_SC_VELOCITY_VECTOR, Z_MARS_SC_VELOCITY_VECTOR, MARS_SC_RADIAL_VELOCITY, MARS_SC_TANGENTIAL_VELOCITY, LOCAL_TRUE_SOLAR_TIME, SOLAR_ZENITH_ANGLE, SC_PITCH_ANGLE, SC_YAW_ANGLE, SC_ROLL_ANGLE, MRO_SAMX_INNER_GIMBAL_ANGLE, MRO_SAMX_OUTER_GIMBAL_ANGLE, MRO_SAPX_INNER_GIMBAL_ANGLE, MRO_SAPX_OUTER_GIMBAL_ANGLE, MRO_HGA_INNER_GIMBAL_ANGLE, MRO_HGA_OUTER_GIMBAL_ANGLE, DES_TEMP, DES_5V, DES_12V, DES_2V5, RX_TEMP, TX_TEMP, TX_LEV, TX_CURR, CORRUPTED_DATA_FLAG);
auxdata = [SCET_BLOCK_WHOLE, SCET_BLOCK_FRAC, EPHEMERIS_TIME, GEOMETRY_EPOCH, SOLAR_LONGITUDE, ORBIT_NUMBER, X_MARS_SC_POSITION_VECTOR, Y_MARS_SC_POSITION_VECTOR, Z_MARS_SC_POSITION_VECTOR, SPACECRAFT_ALTITUDE, SUB_SC_EAST_LONGITUDE, SUB_SC_PLANETOCENTRIC_LATITUDE, SUB_SC_PLANETOGRAPHIC_LATITUDE, X_MARS_SC_VELOCITY_VECTOR, Y_MARS_SC_VELOCITY_VECTOR, Z_MARS_SC_VELOCITY_VECTOR, MARS_SC_RADIAL_VELOCITY, MARS_SC_TANGENTIAL_VELOCITY, LOCAL_TRUE_SOLAR_TIME, SOLAR_ZENITH_ANGLE, SC_PITCH_ANGLE, SC_YAW_ANGLE, SC_ROLL_ANGLE, MRO_SAMX_INNER_GIMBAL_ANGLE, MRO_SAMX_OUTER_GIMBAL_ANGLE, MRO_SAPX_INNER_GIMBAL_ANGLE, MRO_SAPX_OUTER_GIMBAL_ANGLE, MRO_HGA_INNER_GIMBAL_ANGLE, MRO_HGA_OUTER_GIMBAL_ANGLE, DES_TEMP, DES_5V, DES_12V, DES_2V5, TX_TEMP, RX_TEMP, TX_LEV, TX_CURR, CORRUPTED_DATA_FLAG];

%xyz = [X_MARS_SC_POSITION_VECTOR,Y_MARS_SC_POSITION_VECTOR,Z_MARS_SC_POSITION_VECTOR];
%LonLatAlt = [SUB_SC_EAST_LONGITUDE,SUB_SC_PLANETOGRAPHIC_LATITUDE,SPACECRAFT_ALTITUDE];

%dlmwrite(aux_output_name,alldata);
end
