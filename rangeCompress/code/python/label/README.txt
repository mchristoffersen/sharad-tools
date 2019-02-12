DATA PRODUCT README

DESCRIPTION    = "Information on the output data products from rangeCompress.py tool"

geomData       = "Geographic, geometric, and ionospheric properties at each radargram column. Specific
                 format information in geomData.lbl" 
				 
raw            = "Raw, complex-valued range compressed EDR. .npy file format. Can 
                 easily be opened with python numpy library."
				 
amp            = "Absolute value of raw, complex-valued valued compressed EDR. This is equivalent to the 
                 amplitude following range compression (sqrt(re^2 + im^2))"
				 
stack          = "Stacked amplitude. Stacking factor can be changed but is set to a default of 4 traces
                 to avoid incoherent summing."
				 
tiff           = "Output radargram for visualization purposes. This uses the amplitude data output and  
                 performs stacking to a factor of 16 (which can be changed) for data reduction. Data is 
				 plotted in decibels, in reference to the power of a specified noise floor. The decibel
				 power is then scaled between 0 and 255 bytes where the highest power is set at 255."