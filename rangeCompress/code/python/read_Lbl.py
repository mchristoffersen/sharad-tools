#
# Import necessary libraries
#
import os


def lbl_Parse(fname):
  #
  # Define instrument modes
  #
  #
  # Subsurface sounding
  #
  SSInstrMode = { 'SS01': {'Mode': 'SS01', 'Presum': 32, 'BitsPerSample': 8},
                  'SS02': {'Mode': 'SS02','Presum': 28, 'BitsPerSample': 6},
                  'SS03': {'Mode': 'SS03','Presum': 16, 'BitsPerSample': 4},
                  'SS04': {'Mode': 'SS04','Presum': 8, 'BitsPerSample': 8},
                  'SS05': {'Mode': 'SS05','Presum': 4, 'BitsPerSample': 6},
                  'SS06': {'Mode': 'SS06','Presum': 2, 'BitsPerSample': 4},
                  'SS07': {'Mode': 'SS07','Presum': 1, 'BitsPerSample': 8},
                  'SS08': {'Mode': 'SS08','Presum': 32, 'BitsPerSample': 6},
                  'SS09': {'Mode': 'SS09','Presum': 28, 'BitsPerSample': 4},
                  'SS10': {'Mode': 'SS10','Presum': 16, 'BitsPerSample': 8},
                  'SS11': {'Mode': 'SS11','Presum': 8, 'BitsPerSample': 6},
                  'SS12': {'Mode': 'SS12','Presum': 4, 'BitsPerSample': 4},
                  'SS13': {'Mode': 'SS13','Presum': 2, 'BitsPerSample': 8},
                  'SS14': {'Mode': 'SS14','Presum': 1, 'BitsPerSample': 6},
                  'SS15': {'Mode': 'SS15','Presum': 32, 'BitsPerSample': 4},
                  'SS16': {'Mode': 'SS16','Presum': 28, 'BitsPerSample': 8},
                  'SS17': {'Mode': 'SS17','Presum': 16, 'BitsPerSample': 6},
                  'SS18': {'Mode': 'SS18','Presum': 8, 'BitsPerSample': 4},
                  'SS19': {'Mode': 'SS19','Presum': 4, 'BitsPerSample': 8},
                  'SS20': {'Mode': 'SS20','Presum': 2, 'BitsPerSample': 6},
                  'SS21': {'Mode': 'SS21','Presum': 1, 'BitsPerSample': 4},
               }
  #
  # Receive only
  #
  ROInstrMode = { 'RO01': {'Presum': 32, 'BitsPerSample': 8},
                  'RO02': {'Presum': 28, 'BitsPerSample': 6},
                  'RO03': {'Presum': 16, 'BitsPerSample': 4},
                  'RO04': {'Presum': 8, 'BitsPerSample': 8},
                  'RO05': {'Presum': 4, 'BitsPerSample': 6},
                  'RO06': {'Presum': 2, 'BitsPerSample': 4},
                  'RO07': {'Presum': 1, 'BitsPerSample': 8},
                  'RO08': {'Presum': 32, 'BitsPerSample': 6},
                  'RO09': {'Presum': 28, 'BitsPerSample': 4},
                  'RO10': {'Presum': 16, 'BitsPerSample': 8},
                  'RO11': {'Presum': 8, 'BitsPerSample': 6},
                  'RO12': {'Presum': 4, 'BitsPerSample': 4},
                  'RO13': {'Presum': 2, 'BitsPerSample': 8},
                  'RO14': {'Presum': 1, 'BitsPerSample': 6},
                  'RO15': {'Presum': 32, 'BitsPerSample': 4},
                  'RO16': {'Presum': 28, 'BitsPerSample': 8},
                  'RO17': {'Presum': 16, 'BitsPerSample': 6},
                  'RO18': {'Presum': 8, 'BitsPerSample': 4},
                  'RO19': {'Presum': 4, 'BitsPerSample': 8},
                  'RO20': {'Presum': 2, 'BitsPerSample': 6},
                  'RO21': {'Presum': 1, 'BitsPerSample': 4}
                }
  #
  # Now parse LBL File
  #
  if os.path.isfile(fname):
    #
    # Initialize dictionary
    #
    lblDic = {'INSTR_MODE_ID': [],
              'PRI': [],
              'GAIN_CONTROL': [],
              'COMPRESSION': [],
              'RECORD_BYTES': [],
              'FILE_RECORDS': []
              }
    with open(fname) as f:
      lines = f.readlines()
    #
    # Remove end of line characters from list
    #
    lines = [x.rstrip('\n') for x in lines]
    lineCount = len(lines)
    #
    # Remove all blank rows
    #
    lines = [x for x in lines if x]
    print("{} empty lines removed.".format(lineCount - len(lines)))
    lineCount = len(lines)
    #
    # Remove comments
    #
    lines = [x for x in lines if "/*" not in x]
    print("{} comment lines removed.".format(lineCount - len(lines)))
    lineCount = len(lines)
    #
    # Start parsing
    #
    print("Parsing {} lines in LBL file.".format(lineCount))
    for _i in range(lineCount):
      #
      # For this simple test all I should need out of the LBL file are:
      #  INSTRUMENT_MODE_ID
      #
      if lines[_i].split('=')[0].strip() == 'INSTRUMENT_MODE_ID':
        lblDic['INSTR_MODE_ID'] = lines[_i].split('=')[1].strip()
      if lines[_i].split('=')[0].strip() == 'MRO:PULSE_REPETITION_INTERVAL':
        lblDic['PRI'] = lines[_i].split('=')[1].strip()
      if lines[_i].split('=')[0].strip() == 'MRO:MANUAL_GAIN_CONTROL':
        lblDic['GAIN_CONTROL'] = lines[_i].split('=')[1].strip()
      if lines[_i].split('=')[0].strip() == 'MRO:COMPRESSION_SELECTION_FLAG':
        lblDic['COMPRESSION'] = lines[_i].split('=')[1].strip().strip('"')
      if lines[_i].split('=')[0].strip() == 'RECORD_BYTES':
        if lblDic['RECORD_BYTES'] == []:
          lblDic['RECORD_BYTES'] = int(lines[_i].split('=')[1].strip())
      if lines[_i].split('=')[0].strip() == 'FILE_RECORDS':
        if lblDic['FILE_RECORDS'] == []:
          lblDic['FILE_RECORDS'] = int(lines[_i].split('=')[1].strip())
    #
    # Find the instrument mode
    #
    if lblDic['INSTR_MODE_ID'][0:2] == 'SS':
      lblDic['INSTR_MODE_ID'] = SSInstrMode[lblDic['INSTR_MODE_ID']]
    elif lblDic['INSTR_MODE_ID'][0:2] == 'RO':
      lblDic['INSTR_MODE_ID'] = ROInstrMode[lblDic['INSTR_MODE_ID']]
    return lblDic
  else:
    print("{} file not found. Please check path and try again.".format(fname))
    return
