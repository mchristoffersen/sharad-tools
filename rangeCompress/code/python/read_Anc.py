#
# Import necessary libraries
#
import os
import struct
import bitstring
import sys
import numpy as np


def anc_Parse(anc, records):
  """
    This function parses the ancilliary data for an individual SHARAD EDR data record

    Modified: 23Jul18 by Brandon S. Tober to create ancilliary data structure which would parse
    a string of ancilliary data for all records in radar observation
  """

  #
  # Set up dictionary
  #
  ancilliaryData = { 'SCET_BLOCK_WHOLE': [],
                     'SCET_BLOCK_FRAC': [],
                     'TLM_COUNTER': [],
                     'FMT_LENGTH': [],
                     'SPARE1': [],
                     'SCET_OST_WHOLE': [],
                     'SCET_OST_FRAC': [],
                     'SPARE2': [],
                     'OST_LINE_NUMBER': [],
#                     'OST_LINE': [],
                     'OST_LINE_PULSE_REPETITION_INTERVAL': [],
                     'OST_LINE_PHASE_COMPENSATION_TYPE': [],
                     'OST_LINE_SPARE1': [],
                     'OST_LINE_DATA_LENGTH_TAKEN': [],
                     'OST_LINE_OPERATIVE_MODE': [],
                     'OST_LINE_MANUAL_GAIN_CONTROL': [],
                     'OST_LINE_COMPRESSION_SELECTION': [],
                     'OST_LINE_CLOSED_LOOP_TRACKING': [],
                     'OST_LINE_TRACKING_DATA_STORAGE': [],
                     'OST_LINE_TRACKING_PRE_SUMMING': [],
                     'OST_LINE_TRACKING_LOGIC_SELECTION': [],
                     'OST_LINE_THRESHOLD_LOGIC_SELECTION': [],
                     'OST_LINE_SAMPLE_NUMBER': [],
                     'OST_LINE_SPARE2': [],
                     'OST_LINE_ALPHA_BETA': [],
                     'OST_LINE_REFERENCE_BIT': [],
                     'OST_LINE_THRESHOLD': [],
                     'OST_LINE_THRESHOLD_INCREMENT': [],
                     'OST_LINE_SPARE3': [],
                     'OST_LINE_INITIAL_ECHO_VALUE': [],
                     'OST_LINE_EXPECTED_ECHO_SHIFT': [],
                     'OST_LINE_WINDOW_LEFT_SHIFT': [],
                     'OST_LINE_WINDOW_RIGHT_SHIFT': [],
                     'OST_LINE_SPARE4': [],
                     'SPARE3': [],
                     'DATA_BLOCK_ID': [],
                     'SCIENCE_DATA_SOURCE_COUNTER': [],
#                     'PACKET_SEGMENTATION_AND_FPGA_STATUS': [],
                     'PSAFS_SCIENTIFIC_DATA_TYPE': [],
                     'PSAFS_SEGMENTATION_FLAG': [],
                     'PSAFS_SPARE1': [],
                     'PSAFS_SPARE2': [],
                     'PSAFS_DMA_ERROR': [],
                     'PSAFS_TC_OVERRUN': [],
                     'PSAFS_FIFO_FULL': [],
                     'PSAFS_TEST': [],
                     'SPARE4': [],
                     'DATA_BLOCK_FIRST_PRI': [],
                     'TIME_DATA_BLOCK_WHOLE': [],
                     'TIME_DATA_BLOCK_FRAC': [],
                     'SDI_BIT_FIELD': [],
                     'TIME_N': [],
                     'RADIUS_N': [],
                     'TANGENTIAL_VELOCITY_N': [],
                     'RADIAL_VELOCITY_N': [],
                     'TLP': [],
                     'TIME_WPF': [],
                     'DELTA_TIME': [],
                     'TLP_INTERPOLATE': [],
                     'RADIUS_INTERPOLATE': [],
                     'TANGENTIAL_VELOCITY_INTERPOLATE': [],
                     'RADIAL_VELOCITY_INTERPOLATE': [],
                     'END_TLP': [],
                     'S_COEFFS': [],
                     'C_COEFFS': [],
                     'SLOPE': [],
                     'TOPOGRAPHY': [],
                     'PHASE_COMPENSATION_STEP': [],
                     'RECEIVE_WINDOW_OPENING_TIME': [],
                     'RECEIVE_WINDOW_POSITION': [],
                     }

  #
  # Check that length of data is 186 bytes
  #
  if (int(len(anc)) / records) != 186:

    print('Incorrect data supplied. Please ensure data is a 186 byte string')
    sys.exit()
    return
  else:
    #
    # Set up dictionary for items
    #
    for _i in range(records):
      data = anc[_i:((_i+1) * 186)]
      ancilliaryData['SCET_BLOCK_WHOLE'].append(bitstring.BitArray(data[0:4]).uint)
      ancilliaryData['SCET_BLOCK_FRAC'].append(bitstring.BitArray(data[4:6]).uint)
      ancilliaryData['TLM_COUNTER'].append(struct.unpack('>I', data[6:10])[0])
      ancilliaryData['FMT_LENGTH'].append(struct.unpack('>H', data[10:12])[0])
      ancilliaryData['SPARE1'].append(struct.unpack('>H', data[12:14])[0])
      ancilliaryData['SCET_OST_WHOLE'].append(struct.unpack('>I', data[14:18])[0])
      ancilliaryData['SCET_OST_FRAC'].append(struct.unpack('>H', data[18:20])[0])
      ancilliaryData['SPARE2'].append(struct.unpack('>B', data[20:21])[0])
      ancilliaryData['OST_LINE_NUMBER'].append(struct.unpack('>B', data[21:22])[0])
      #
      # OST_LINE_NUMBER BIT STRING
      #
      OST_LINE = bitstring.BitArray(data[22:39])
      ancilliaryData['OST_LINE_PULSE_REPETITION_INTERVAL'].append(OST_LINE[0:4].uint)
      ancilliaryData['OST_LINE_PHASE_COMPENSATION_TYPE'].append(OST_LINE[4:8].uint)
      ancilliaryData['OST_LINE_SPARE1'].append(OST_LINE[8:10].uint)
      ancilliaryData['OST_LINE_DATA_LENGTH_TAKEN'].append(OST_LINE[10:32].uint)
      ancilliaryData['OST_LINE_OPERATIVE_MODE'].append(OST_LINE[32:40].uint)
      ancilliaryData['OST_LINE_MANUAL_GAIN_CONTROL'].append(OST_LINE[40:48].uint)
      ancilliaryData['OST_LINE_COMPRESSION_SELECTION'].append(OST_LINE[48:49].bool)
      ancilliaryData['OST_LINE_CLOSED_LOOP_TRACKING'].append(OST_LINE[49:50].bool)
      ancilliaryData['OST_LINE_TRACKING_DATA_STORAGE'].append(OST_LINE[50:51].bool)
      ancilliaryData['OST_LINE_TRACKING_PRE_SUMMING'].append(OST_LINE[51:54].uint)
      ancilliaryData['OST_LINE_TRACKING_LOGIC_SELECTION'].append(OST_LINE[54:55].uint)
      ancilliaryData['OST_LINE_THRESHOLD_LOGIC_SELECTION'].append(OST_LINE[55:56].uint)
      ancilliaryData['OST_LINE_SAMPLE_NUMBER'].append(OST_LINE[56:60].uint)
      ancilliaryData['OST_LINE_SPARE2'].append(OST_LINE[60:61].uint)
      ancilliaryData['OST_LINE_ALPHA_BETA'].append(OST_LINE[61:63].uint)
      ancilliaryData['OST_LINE_REFERENCE_BIT'].append(OST_LINE[63:64].uint)
      ancilliaryData['OST_LINE_THRESHOLD'].append(OST_LINE[64:72].uint)
      ancilliaryData['OST_LINE_THRESHOLD_INCREMENT'].append(OST_LINE[72:80].uint)
      ancilliaryData['OST_LINE_SPARE3'].append(OST_LINE[80:84].uint)
      ancilliaryData['OST_LINE_INITIAL_ECHO_VALUE'].append(OST_LINE[84:87].uint)
      ancilliaryData['OST_LINE_EXPECTED_ECHO_SHIFT'].append(OST_LINE[87:90].uint)
      ancilliaryData['OST_LINE_WINDOW_LEFT_SHIFT'].append(OST_LINE[90:93].uint)
      ancilliaryData['OST_LINE_WINDOW_RIGHT_SHIFT'].append(OST_LINE[93:96].uint)
      ancilliaryData['OST_LINE_SPARE4'].append(OST_LINE[96:128].uint)
      ancilliaryData['SPARE3'].append(struct.unpack('>B', data[38:39])[0])
      ancilliaryData['DATA_BLOCK_ID'].append(bitstring.BitArray(data[39:42]).uint)
      ancilliaryData['SCIENCE_DATA_SOURCE_COUNTER'].append(struct.unpack('>H', data[42:44])[0])
      #
      # PACKET_SEGMENTATION_AND_FPGA_STATUS bit string
      #
      PSAFS = bitstring.BitArray(data[44:46])
      ancilliaryData['PSAFS_SCIENTIFIC_DATA_TYPE'].append(PSAFS[0:1].uint)
      ancilliaryData['PSAFS_SEGMENTATION_FLAG'].append(PSAFS[1:3].uint)
      ancilliaryData['PSAFS_SPARE1'].append(PSAFS[3:8].uint)
      ancilliaryData['PSAFS_SPARE2'].append(PSAFS[8:12].uint)
      ancilliaryData['PSAFS_DMA_ERROR'].append(PSAFS[12:13].uint)
      ancilliaryData['PSAFS_TC_OVERRUN'].append(PSAFS[13:14].uint)
      ancilliaryData['PSAFS_FIFO_FULL'].append(PSAFS[14:15].uint)
      ancilliaryData['PSAFS_TEST'].append(PSAFS[15:16].uint)
      #
      #
      #
      ancilliaryData['SPARE4'].append(struct.unpack('>B', data[46:47])[0])
      ancilliaryData['DATA_BLOCK_FIRST_PRI'].append(bitstring.BitArray(data[47:50]).uint)
      ancilliaryData['TIME_DATA_BLOCK_WHOLE'].append(struct.unpack('>I', data[50:54])[0])
      ancilliaryData['TIME_DATA_BLOCK_FRAC'].append(struct.unpack('>H', data[54:56])[0])
      ancilliaryData['SDI_BIT_FIELD'].append(struct.unpack('>H', data[56:58])[0])
      ancilliaryData['TIME_N'].append(struct.unpack('>f', data[58:62])[0])
      ancilliaryData['RADIUS_N'].append(struct.unpack('>f', data[62:66])[0])
      ancilliaryData['TANGENTIAL_VELOCITY_N'].append(struct.unpack('>f', data[66:70])[0])
      ancilliaryData['RADIAL_VELOCITY_N'].append(struct.unpack('>f', data[70:74])[0])
      ancilliaryData['TLP'].append(struct.unpack('>f', data[74:78])[0])
      ancilliaryData['TIME_WPF'].append(struct.unpack('>f', data[78:82])[0])
      ancilliaryData['DELTA_TIME'].append(struct.unpack('>f', data[82:86])[0])
      ancilliaryData['TLP_INTERPOLATE'].append(struct.unpack('>f', data[86:90])[0])
      ancilliaryData['RADIUS_INTERPOLATE'].append(struct.unpack('>f', data[90:94])[0])
      ancilliaryData['TANGENTIAL_VELOCITY_INTERPOLATE'].append(struct.unpack('>f', data[94:98])[0])
      ancilliaryData['RADIAL_VELOCITY_INTERPOLATE'].append(struct.unpack('>f', data[98:102])[0])
      ancilliaryData['END_TLP'].append(struct.unpack('>f', data[102:106])[0])
      ancilliaryData['S_COEFFS'].append(np.array([struct.unpack('>f', data[106:110]),
                                         struct.unpack('>f', data[110:114]),
                                         struct.unpack('>f', data[114:118]),
                                         struct.unpack('>f', data[118:122]),
                                         struct.unpack('>f', data[122:126]),
                                         struct.unpack('>f', data[126:130]),
                                         struct.unpack('>f', data[130:134]),
                                         struct.unpack('>f', data[134:138])
                                        ]))
      ancilliaryData['C_COEFFS'].append(np.array([struct.unpack('>f', data[138:142]),
                                         struct.unpack('>f', data[142:146]),
                                         struct.unpack('>f', data[146:150]),
                                         struct.unpack('>f', data[150:154]),
                                         struct.unpack('>f', data[154:158]),
                                         struct.unpack('>f', data[158:162]),
                                         struct.unpack('>f', data[162:166])
                                        ]))
      ancilliaryData['SLOPE'].append(struct.unpack('>f', data[166:170])[0])
      ancilliaryData['TOPOGRAPHY'].append(struct.unpack('>f', data[170:174])[0])
      ancilliaryData['PHASE_COMPENSATION_STEP'].append(struct.unpack('>f', data[174:178])[0])
      ancilliaryData['RECEIVE_WINDOW_OPENING_TIME'].append(struct.unpack('>f', data[178:182])[0])
      ancilliaryData['RECEIVE_WINDOW_POSITION'].append(struct.unpack('>f', data[182:186])[0])
      print(struct.unpack('<f',data[178:182]))
    #####################################################################################
    #
    # PACKET_SEGMENTATION_AND_FPGA_STATUS bit string
    #
##      PSAFS = bitstring.BitArray(data[44:46])
##      ancilliaryData['PSAFS_SCIENTIFIC_DATA_TYPE'].append(PSAFS[0:1].uint)
##      ancilliaryData['PSAFS_SEGMENTATION_FLAG'].append(PSAFS[1:3].uint)
##      ancilliaryData['PSAFS_SPARE1'].append(PSAFS[3:8].uint)
##      ancilliaryData['PSAFS_SPARE2'].append(PSAFS[8:12].uint)
##      ancilliaryData['PSAFS_DMA_ERROR'].append(PSAFS[12:13].uint)
##      ancilliaryData['PSAFS_TC_OVERRUN'].append(PSAFS[13:14].uint)
##      ancilliaryData['PSAFS_FIFO_FULL'].append(PSAFS[14:15].uint)
##      ancilliaryData['PSAFS_TEST'].append(PSAFS[15:16].uint)
##      #####################################################################################
      #
      # OST_LINE_NUMBER BIT STRING
      #
##      OST_LINE = bitstring.BitArray(data[22:39])
##      ancilliaryData['OST_LINE_PULSE_REPETITION_INTERVAL'].append(OST_LINE[0:4].uint)
##      ancilliaryData['OST_LINE_PHASE_COMPENSATION_TYPE'].append(OST_LINE[4:8].uint)
##      ancilliaryData['OST_LINE_SPARE1'].append(OST_LINE[8:10].uint)
##      ancilliaryData['OST_LINE_DATA_LENGTH_TAKEN'].append(OST_LINE[10:32].uint)
##      ancilliaryData['OST_LINE_OPERATIVE_MODE'].append(OST_LINE[32:40].uint)
##      ancilliaryData['OST_LINE_MANUAL_GAIN_CONTROL'].append(OST_LINE[40:48].uint)
##      ancilliaryData['OST_LINE_COMPRESSION_SELECTION'].append(OST_LINE[48:49].bool)
##      ancilliaryData['OST_LINE_CLOSED_LOOP_TRACKING'].append(OST_LINE[49:50].bool)
##      ancilliaryData['OST_LINE_TRACKING_DATA_STORAGE'].append(OST_LINE[50:51].bool)
##      ancilliaryData['OST_LINE_TRACKING_PRE_SUMMING'].append(OST_LINE[51:54].uint)
##      ancilliaryData['OST_LINE_TRACKING_LOGIC_SELECTION'].append(OST_LINE[54:55].uint)
##      ancilliaryData['OST_LINE_THRESHOLD_LOGIC_SELECTION'].append(OST_LINE[55:56].uint)
##      ancilliaryData['OST_LINE_SAMPLE_NUMBER'].append(OST_LINE[56:60].uint)
##      ancilliaryData['OST_LINE_SPARE2'].append(OST_LINE[60:61].uint)
##      ancilliaryData['OST_LINE_ALPHA_BETA'].append(OST_LINE[61:63].uint)
##      ancilliaryData['OST_LINE_REFERENCE_BIT'].append(OST_LINE[63:64].uint)
##      ancilliaryData['OST_LINE_THRESHOLD'].append(OST_LINE[64:72].uint)
##      ancilliaryData['OST_LINE_THRESHOLD_INCREMENT'].append(OST_LINE[72:80].uint)
##      ancilliaryData['OST_LINE_SPARE3'].append(OST_LINE[80:84].uint)
##      ancilliaryData['OST_LINE_INITIAL_ECHO_VALUE'].append(OST_LINE[84:87].uint)
##      ancilliaryData['OST_LINE_EXPECTED_ECHO_SHIFT'].append(OST_LINE[87:90].uint)
##      ancilliaryData['OST_LINE_WINDOW_LEFT_SHIFT'].append(OST_LINE[90:93].uint)
##      ancilliaryData['OST_LINE_WINDOW_RIGHT_SHIFT'].append(OST_LINE[93:96].uint)
##      ancilliaryData['OST_LINE_SPARE4'].append(OST_LINE[96:128].uint)
  return ancilliaryData
