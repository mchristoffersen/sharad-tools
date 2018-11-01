from __future__ import division, print_function

import numpy as np, pandas as pd
import pickle
from bitstring import *

###########################################################################
### additional processors
identity = lambda x: x
extract3Doubles = lambda x: np.fromstring(x, count=3, dtype='float64')
#extract512Floats = lambda x: np.fromstring(x, count=512, dtype='float32')
asUTF8string = lambda x: x.decode('utf-8')

def extract512ComplexFloats(d):
    data=np.fromstring(d, count=1024, dtype='float32')
    assert data.shape == (1024, )
    data=data[0:512] * np.exp(1j* data[512:])
    data=data.astype('complex128')
    data.shape=[1, 512]
    return data

################# see R_SS3_TRK_CMP.FMT for all metadata
SS3_RECORD_BYTES=24823
SS3_RECORD_ITEMS=[
        ("CENTRAL_FREQUENCY_ch1", "floatle:32", identity),
        ("CENTRAL_FREQUENCY_ch2", "floatle:32", identity),
        ("SLOPE", "floatle:32", identity),
        ("SCET_FRAME_WHOLE", "uintle:32", identity),
        ("SCET_FRAME_FRAC", "uintle:16", identity),
        ("H_SCET_PAR", "floatle:32", identity),
        ("VT_SCET_PAR", "floatle:32", identity),
        ("VR_SCET_PAR", "floatle:32", identity),
        ("DELTA_S_SCET_PAR", "floatle:32", identity),
        ("NA_SCET_PAR_ch1", "uintle:16", identity),
        ("NA_SCET_PAR_ch2", "uintle:16", identity),
# assemble complex data in-place
        ("ECHO_MINUS1_F1", "bytes:4096", extract512ComplexFloats),
        ("ECHO_ZERO_F1", "bytes:4096",   extract512ComplexFloats),
        ("ECHO_PLUS1_F1", "bytes:4096",  extract512ComplexFloats),
        ("ECHO_MINUS1_F2", "bytes:4096", extract512ComplexFloats),
        ("ECHO_ZERO_F2", "bytes:4096",   extract512ComplexFloats),
        ("ECHO_PLUS1_F2", "bytes:4096",  extract512ComplexFloats),
#        ("ECHO_MODULUS_MINUS1_F1_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_PHASE_MINUS1_F1_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_MODULUS_ZERO_F1_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_PHASE_ZERO_F1_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_MODULUS_PLUS1_F1_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_PHASE_PLUS1_F1_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_MODULUS_MINUS1_F2_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_PHASE_MINUS1_F2_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_MODULUS_ZERO_F2_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_PHASE_ZERO_F2_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_MODULUS_PLUS1_F2_DIP", "bytes:2048", extract512Floats),
#        ("ECHO_PHASE_PLUS1_F2_DIP", "bytes:2048", extract512Floats),
        ("GEOMETRY_EPHEMERIS_TIME", "floatle:64", identity),
        ("GEOMETRY_EPOCH", "bytes:23", asUTF8string),
        ("MARS_SOLAR_LONGITUDE", "floatle:64", identity),
        ("MARS_SUN_DISTANCE", "floatle:64", identity),
        ("ORBIT_NUMBER", "uintle:32", identity),
        ("TARGET_NAME", "bytes:6", asUTF8string),
        ("TARGET_SC_POSITION_VECTOR", "bytes:24", extract3Doubles),
        ("SPACECRAFT_ALTITUDE", "floatle:64", identity),
        ("SUB_SC_LONGITUDE", "floatle:64", identity),
        ("SUB_SC_LATITUDE", "floatle:64", identity),
        ("TARGET_SC_VELOCITY_VECTOR", "bytes:24", extract3Doubles),
        ("TARGET_SC_RADIAL_VELOCITY", "floatle:64", identity),
        ("TARGET_SC_TANG_VELOCITY", "floatle:64", identity),
        ("LOCAL_TRUE_SOLAR_TIME", "floatle:64", identity),
        ("SOLAR_ZENITH_ANGLE", "floatle:64", identity),
        ("DIPOLE_UNIT_VECTOR", "bytes:24", extract3Doubles),
        ("MONOPOLE_UNIT_VECTOR", "bytes:24", extract3Doubles),
]

###########################################################################
# parse
def parse_RECORD(record, idx):

    # extract format description
    fmts=[ i[1] for i in SS3_RECORD_ITEMS ]
    bs=ConstBitStream(record)

    data={ }
    for name, fmt, processor in SS3_RECORD_ITEMS:
        obp=bs.bytepos
        theitem=processor(bs.read(fmt))
        data[name]=theitem
        #print('%5i %3i %s %s'%(obp+1, len(data), name, str(theitem)[0:40]))

    assert bs.bytepos == SS3_RECORD_BYTES
    assert len(data) == len(SS3_RECORD_ITEMS)

    return data

###########################################################################
def load_E_SS3(filename):

    buf=None
    with open(filename, 'rb') as f:
        buf=f.read()
    assert buf is not None

    # maybe we can win by truncating too long files from the beginning
    # use assert for now
    assert len(buf)%SS3_RECORD_BYTES == 0
    remainder=len(buf)%SS3_RECORD_BYTES

    # get number of records
    nrec=len(buf)//SS3_RECORD_BYTES

    records=[ parse_RECORD(buf[i:i+SS3_RECORD_BYTES], i)
              for i in range(0, len(buf)-1, SS3_RECORD_BYTES) ]

    return records


###########################################################################

if __name__=='__main__':
    import sys

    assert len(sys.argv) == 2
    thedata=load_E_SS3(sys.argv[1])

    thedata=pd.DataFrame(thedata)
    thedata.to_pickle('%s.pickle'%sys.argv[1], compression='xz')

