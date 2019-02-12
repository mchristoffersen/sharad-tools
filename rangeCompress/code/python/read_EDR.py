#
# Import necessary libraries
#
import numpy as np
import matplotlib.pyplot as plt
import bitstring, sys


def EDR_Parse(fname, records, recLen, bps):

  """
  This function reads a single EDR record and returns the ancilliary
  and science data. Data are read and decoded based off their bit resolution
  Input:
      _file: File object identifier pointing to the data file containing the binary data
  Output:
      ancil: Data dictionary containing all the information parsed from the ancilliary data for the record
      echoes: Decoded science data

  Modified: 27Aug18 by Brandon S. Tober to read entire EDR science record at once into data matrix. 
    also modified so that bitstring is only used for observations where bps is 4 or 6. 8 bit samples can be read using np.fromstring much faster.
  """
  #
  # Create matrix to store parsed data
  #
  decodedData = np.zeros([3600, records], dtype = "int64")
  #
  # Open binary data science file
  #
  _file = open(fname, 'rb')
  #
  # Make sure we are at the beginning of a record
  #
  _file.seek(0)
  #
  # Read in entire binary data volume for all traces
  #
  rawData = _file.read(recLen * records)
  #
  # Partition data volume by trace
  #
  ancil = b''
  for n in range(records):
    #
    # Separate ancil and echo data
    #
    ancil += rawData[(n * recLen):((n * recLen) + 186)]
    echoes = rawData[((n * recLen) + 186):((n + 1) * recLen)]

    # if n == 0:
    #   ancil = rawData[(n * recLen):(186 * (n + 1))]
    #   echoes = rawData[(186 * (n + 1)):recLen]
    # else:
    #   ancil = ancil + rawData[(n * recLen):((n * recLen) + 186)]
    #   echoes = rawData[((n * recLen) + 186):(recLen * (n +1))]
    # Okay, now decode the data
    # For 8-bit samples, there is a sample for every byte
    # For 6-bit samples, there are 2 samples for every 3 bytes
    # For 4-bit samples, there are 2 samples for every byte
    #
    # Making the vector have 4096 rows is to allow for proper decovolution of the
    # calibrated chirp
    #
    # Step 4: Decode the science data based on the bit resolution
    #
    # Break Byte stream into Bit Stream
    # This isn't necessary for the 8-bit resolution, but to keep the code
    # clean, split the bytes up regardless of resolution
    #
    if bps == 4 or bps == 6:
      b = bitstring.BitArray(echoes)
      for _j in range(0, len(b), bps):
        decodedData[int(_j/bps),n] = b[_j:_j+bps].int
    elif bps == 8:
      decodedData[:,n] = np.fromstring(echoes, dtype = np.int8)
  return decodedData, ancil


def sci_Decompress(data, compression, presum, bps, SDI):    #

  """
    This function decompresses the data based off page 8 of the
    SHALLOW RADAR EXPERIMENT DATA RECORD SOFTWARE INTERFACE SPECIFICATION.

    Modified: 23Jul18 by Brandon S. Tober to create decompress entire data matrix at once

    If the compression type is 'Static'
       U = C*2**S / N
         C is the Compressed Data
         S = L - R + 8
            L is base 2 log of N rounded UP to the nearest integer
            R is the bit resolution of the compressed values
         N is the number of pre-summed echoes
    If the compression type is 'dynamic'
      NOT WORKING YET
      U = C*2**S/N
        C is the compressed data
        N is the number of pre-summed echoes
        S = SDI for SDI <= 5
        S = SDI-6 for 5 < SDI <= 16
        S = SDI-16 for SDI > 16
          where SDI is the SDI_BIT_FIELD parameter from ANCILLIARY DATA
  """
  # Step 5: Decompress the data
  # Note: Only Static decompression works at this time
  #
  # Get shape of data structure
  #
  S = np.zeros(data.shape[1], dtype = "float64")
  if compression == 'STATIC' or compression == 'DYNAMIC':
    #
    # Handle fixed scaling
    #
    if compression == 'STATIC': # Static scaling
      L = np.ceil(np.log2(int(presum)))
      R = bps
      S = L - R + 8
      N = presum
      decomp = np.power(2, S) / N
      decompressedData = np.multiply(data,decomp)
      #decompressedData[:,:] = data[:,:] * decomp
      #decompressed_data = data * decomp

    elif compression == True:#dynamic scaling
      decomp = np.zeros(data.shape[1], dtype = "float64")
      N = presum
      for n in len(SDI):
        if SDI[n] <= 5:
          S[n] = SDI[n]
        elif 5 < SDI[n] <= 16:
          S[n] = SDI[n] - 6
        elif SDI[n] > 16:
          S[n] = SDI[n] - 16
      decomp[:] = np.power(2, S[:]) / N
      decompressedData = np.multiply(data,decomp)
    return decompressedData

  else:
    print('Decompression Error: Compression Type {} not understood'.format(compression))
    return
