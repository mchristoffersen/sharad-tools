# import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy

def rgram(amp, path, runName, chirp, windowName, rel = True):
    """
    function designed to create radargrams for visualization purposes from range compressed EDRs
    this data is scaled by the noise level, so is purely for visualization.

    github: b-tober
    Updated by: Brandon S. Tober
    Last Updated: 10Jan2019
    """
    pow = np.power(amp,2)
    noise_floor = np.mean(pow[:50,:])
    dB  = 10 * np.log10(pow / noise_floor) 
    if rel == True:
        # find max dB value for each trace in data
        maxdB = np.amax(dB, axis = 0)
    else:
        # find overall max dB value
        maxdB = np.amax(dB)

    rgram = dB / maxdB * 255

    # zero out values below noise floor and clip values greater than maxdB
    rgram[np.where(rgram < 0)] = 0.
    rgram[np.where(rgram > 255)] = 255.
    imName = path + 'processed/browse/tiff/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '_' + chirp + '_' + windowName + '_slc.tiff'
    try:
        plt.imsave(imName, rgram, cmap = 'gray')
    except Exception as err:
        print(err)
        print('Reducing data to save radargram')
        try:
            rgram = rgram[:,::8]
            plt.clf()
            plt.close()
            plt.imsave(imName, rgram, cmap='gray')
        except Exception as err:
                print(err)
    return
