#
# Import necessary libraries
#
import pandas as pd
import os
import struct

def aux_Parse(fname, df=False):
  """
  length from label filke
  This function will read in the auxilliary file and return a pandas
  dataframe with the necessary data
  Saving the below NUMPY dtype formatting in the event I can actually
  get it to work...
  dt = np.dtype([('SCET_BLOCK_WHOLE', 'u4'),
                ('SCET_BLOCK_FRAC', 'u2'),
                ('EPHEMERIS_TIME', 'f8'),
                ('GEOMETRY_EPOCH', 'U23'),
                ('SOLAR_LONGITUDE', 'f8'),
                ('ORBIT_NUMBER', 'i4'),
                ('X_MARS_SC_POSITION_VECTOR', 'f8'),
                ('Y_MARS_SC_POSITION_VECTOR', 'f8'),
                ('Z_MARS_SC_POSITION_VECTOR', 'f8'),
                ('SPACECRAFT_ALTITUDE', 'f8'),
                ('SUB_SC_EAST_LONGITUDE', 'f8'),
                ('SUB_SC_PLANETOCENTRIC_LATITUDE', 'f8'),
                ('SUB_SC_PLANETOGRAPHIC_LATITUDE', 'f8'),
                ('X_MARS_SC_VELOCITY_VECTOR', 'f8'),
                ('Y_MARS_SC_VELOCITY_VECTOR', 'f8'),
                ('Z_MARS_SC_VELOCITY_VECTOR', 'f8'),
                ('MARS_SC_RADIAL_VELOCITY', 'f8'),
                ('MARS_SC_TANGENTIAL_VELOCITY', 'f8'),
                ('LOCAL_TRUE_SOLAR_TIME', 'f8'),
                ('SOLAR_ZENITH_ANGLE', 'f8'),
                ('SC_PITCH_ANGLE', 'f8'),
                ('SC_YAW_ANGLE', 'f8'),
                ('SC_ROLL_ANGLE', 'f8'),
                ('MRO_SAMX_INNER_GIMBAL_ANGLE', 'f8'),
                ('MRO_SAMX_OUTER_GIMBAL_ANGLE', 'f8'),
                ('MRO_SAPX_INNER_GIMBAL_ANGLE', 'f8'),
                ('MRO_SAPX_OUTER_GIMBAL_ANGLE', 'f8'),
                ('MRO_HGA_INNER_GIMBAL_ANGLE', 'f8'),
                ('MRO_HGA_OUTER_GIMBAL_ANGLE', 'f8'),
                ('DES_TEMP', 'f4'),
                ('DES_5V', 'f4'),
                ('DES_12V', 'f4'),
                ('DES_2V5', 'f4'),
                ('RX_TEMP', 'f4'),
                ('TX_TEMP', 'f4'),
                ('TX_LEV', 'f4'),
                ('TX_CURR', 'f4'),
                ('CORRUPTED_DATA_FLAG', 'i2')
               ]
               )
  """
  #
  # Set up dictionary
  #
  auxData ={'SCET_BLOCK_WHOLE': [],
            'SCET_BLOCK_FRAC': [],
            'EPHEMERIS_TIME': [],
            'ELAPSED_TIME': [],
            'GEOMETRY_EPOCH': [],
            'SOLAR_LONGITUDE': [],
            'ORBIT_NUMBER': [],
            'X_MARS_SC_POSITION_VECTOR': [],
            'Y_MARS_SC_POSITION_VECTOR': [],
            'Z_MARS_SC_POSITION_VECTOR': [],
            'SPACECRAFT_ALTITUDE': [],
            'SUB_SC_EAST_LONGITUDE': [],
            'SUB_SC_PLANETOCENTRIC_LATITUDE': [],
            'SUB_SC_PLANETOGRAPHIC_LATITUDE': [],
            'X_MARS_SC_VELOCITY_VECTOR': [],
            'Y_MARS_SC_VELOCITY_VECTOR': [],
            'Z_MARS_SC_VELOCITY_VECTOR': [],
            'MARS_SC_RADIAL_VELOCITY': [],
            'MARS_SC_TANGENTIAL_VELOCITY': [],
            'LOCAL_TRUE_SOLAR_TIME': [],
            'SOLAR_ZENITH_ANGLE': [],
            'SC_PITCH_ANGLE': [],
            'SC_YAW_ANGLE': [],
            'SC_ROLL_ANGLE': [],
            'MRO_SAMX_INNER_GIMBAL_ANGLE': [],
            'MRO_SAMX_OUTER_GIMBAL_ANGLE': [],
            'MRO_SAPX_INNER_GIMBAL_ANGLE': [],
            'MRO_SAPX_OUTER_GIMBAL_ANGLE': [],
            'MRO_HGA_INNER_GIMBAL_ANGLE': [],
            'MRO_HGA_OUTER_GIMBAL_ANGLE': [],
            'DES_TEMP': [],
            'DES_5V': [],
            'DES_12V': [],
            'DES_2V5': [],
            'RX_TEMP': [],
            'TX_TEMP': [],
            'TX_LEV': [],
            'TX_CURR': [],
            'CORRUPTED_DATA_FLAG': []
          }
  #
  # Each record is composed of 267 bytes
  #
  recLen = 267
  if os.path.isfile(fname):
    _file = open(fname, 'rb')
    fsize = os.path.getsize(fname)
    for _i in range(int(fsize/recLen)): # Go through all the rows
      _file.seek(_i*recLen)
      rawData = _file.read(recLen)
      auxData['SCET_BLOCK_WHOLE'].append(struct.unpack(">I", rawData[0:4])[0])
      auxData['SCET_BLOCK_FRAC'].append(struct.unpack(">H", rawData[4:6])[0])
      auxData['EPHEMERIS_TIME'].append(struct.unpack(">d", rawData[6:14])[0])
      auxData['ELAPSED_TIME'].append(auxData['EPHEMERIS_TIME'][_i] - auxData['EPHEMERIS_TIME'][0])
      auxData['GEOMETRY_EPOCH'].append(rawData[14:37].decode("utf-8"))
      auxData['SOLAR_LONGITUDE'].append(struct.unpack(">d", rawData[37:45])[0])
      auxData['ORBIT_NUMBER'].append(struct.unpack(">i", rawData[45:49])[0])
      auxData['X_MARS_SC_POSITION_VECTOR'].append(struct.unpack(">d", rawData[49:57])[0])
      auxData['Y_MARS_SC_POSITION_VECTOR'].append(struct.unpack(">d", rawData[57:65])[0])
      auxData['Z_MARS_SC_POSITION_VECTOR'].append(struct.unpack(">d", rawData[65:73])[0])
      auxData['SPACECRAFT_ALTITUDE'].append(struct.unpack(">d", rawData[73:81])[0])
      auxData['SUB_SC_EAST_LONGITUDE'].append(struct.unpack(">d", rawData[81:89])[0])
      auxData['SUB_SC_PLANETOCENTRIC_LATITUDE'].append(struct.unpack(">d", rawData[89:97])[0])
      auxData['SUB_SC_PLANETOGRAPHIC_LATITUDE'].append(struct.unpack(">d", rawData[97:105])[0])
      auxData['X_MARS_SC_VELOCITY_VECTOR'].append(struct.unpack(">d", rawData[105:113])[0])
      auxData['Y_MARS_SC_VELOCITY_VECTOR'].append(struct.unpack(">d", rawData[113:121])[0])
      auxData['Z_MARS_SC_VELOCITY_VECTOR'].append(struct.unpack(">d", rawData[121:129])[0])
      auxData['MARS_SC_RADIAL_VELOCITY'].append(struct.unpack(">d", rawData[129:137])[0])
      auxData['MARS_SC_TANGENTIAL_VELOCITY'].append(struct.unpack(">d", rawData[137:145])[0])
      auxData['LOCAL_TRUE_SOLAR_TIME'].append(struct.unpack(">d", rawData[145:153])[0])
      auxData['SOLAR_ZENITH_ANGLE'].append(struct.unpack(">d", rawData[153:161])[0])
      auxData['SC_PITCH_ANGLE'].append(struct.unpack(">d", rawData[161:169])[0])
      auxData['SC_YAW_ANGLE'].append(struct.unpack(">d", rawData[169:177])[0])
      auxData['SC_ROLL_ANGLE'].append(struct.unpack(">d", rawData[177:185])[0])
      auxData['MRO_SAMX_INNER_GIMBAL_ANGLE'].append(struct.unpack(">d", rawData[185:193])[0])
      auxData['MRO_SAMX_OUTER_GIMBAL_ANGLE'].append(struct.unpack(">d", rawData[193:201])[0])
      auxData['MRO_SAPX_INNER_GIMBAL_ANGLE'].append(struct.unpack(">d", rawData[201:209])[0])
      auxData['MRO_SAPX_OUTER_GIMBAL_ANGLE'].append(struct.unpack(">d", rawData[209:217])[0])
      auxData['MRO_HGA_INNER_GIMBAL_ANGLE'].append(struct.unpack(">d", rawData[217:225])[0])
      auxData['MRO_HGA_OUTER_GIMBAL_ANGLE'].append(struct.unpack(">d", rawData[225:233])[0])
      auxData['DES_TEMP'].append(struct.unpack(">f", rawData[233:237])[0])
      auxData['DES_5V'].append(struct.unpack(">f", rawData[237:241])[0])
      auxData['DES_12V'].append(struct.unpack(">f", rawData[241:245])[0])
      auxData['DES_2V5'].append(struct.unpack(">f", rawData[245:249])[0])
      auxData['RX_TEMP'].append(struct.unpack(">f", rawData[249:253])[0])
      auxData['TX_TEMP'].append(struct.unpack(">f", rawData[253:257])[0])
      auxData['TX_LEV'].append(struct.unpack(">f", rawData[257:261])[0])
      auxData['TX_CURR'].append(struct.unpack(">f", rawData[261:265])[0])
      auxData['CORRUPTED_DATA_FLAG'].append(struct.unpack(">h", rawData[265:267])[0])
    #
    # Check if wanting dataframe returned
    #
    if df:
      auxData = pd.DataFrame.from_dict(auxData)
    return auxData


def makeAuxPlots(df):
  """
    Something I can do later
  """
  f, axarr = plt.subplots(2, sharex=True)
  f.suptitle('Sharing X axis')
  X = df['ELAPSED_TIME']
  axarr[0].plot(X, df['SOLAR_LONGITUDE'], 'k.')
  axarr[1].plot(X, df['X_MARS_SC_POSITION_VECTOR'], 'k.')
  axarr[1].plot(X, df['Y_MARS_SC_POSITION_VECTOR'], 'r.')
  axarr[1].plot(X, df['Z_MARS_SC_POSITION_VECTOR'], 'b.')
  plt.show()
  return
