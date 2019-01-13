# import necessary libraries
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import scipy

def rgram(amp, path, runName, chirp, windowName, rel = True):
    """
    function designed to create radargrams for visualization purposes from range compressed EDRs
    this data is scaled by the noise level, so is purely for visualization.

    github: b-tober
    Updated by: Brandon S. Tober
    Last Updated: 11Jan2019
    """
    # stack data to reduce for visualization
    stackFac = 16
    stackCols = int(np.ceil(amp.shape[1]/stackFac))
    ampStack = np.zeros((3600, stackCols))   
    for _i in range(stackCols - 1):
        ampStack[:,_i] = np.mean(amp[:,stackFac*_i:stackFac*(_i+1)], axis = 1)
    # account for traces left if number of traces is not divisible by stackFac
    ampStack[:,-1] = np.mean(amp[:,stackFac*(_i+1):-1], axis = 1)

    pow = np.power(ampStack,2)                  # convert stacked amplitude to power
    noise_floor = np.mean(pow[:50,:])           # define a noise floor from average power of flattened first 50 rows
    dB  = 10 * np.log10(pow / noise_floor)      # convert power to dB in reference to noise floor
    if rel == True:
        # find max dB value for each trace in data
        maxdB = np.amax(dB, axis = 0)
    else:
        # find overall max dB value
        maxdB = np.amax(dB)

    rgram = dB / maxdB * 255                    # scale radargram from 0 to 255 based on max dB

    # zero out values below noise floor and clip values greater than maxdB
    rgram[np.where(rgram < 0)] = 0.
    rgram[np.where(rgram > 255)] = 255.
    # rgram = Image.fromarray(rgram)
    imName = path + 'processed/browse/tiff/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + chirp + '_' + windowName + '_slc.tiff'
    try:
        # rgram.save(imName)
        plt.imsave(imName, rgram, cmap = 'gray')
    except Exception as err:
        print(err)
    return
