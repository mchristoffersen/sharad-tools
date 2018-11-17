# import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy

def rgram(data, path, runName, rel = True):
    pow = np.power(np.abs(data),2)
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
    imName = path + 'processed/browse/tiff/' + runName.split('_')[1] + '_' + runName.split('_')[2] + '.tiff'
    try:
        plt.imsave(imName, rgram, cmap = 'gray')
    except Exception as err:
        print(err)
    return
