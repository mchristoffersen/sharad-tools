This repo contains python scripts for extracting the first return power from SHARAD radar data. Currently this includes two different scripts for working with FPB data from the PDS, or pulse-compressed EDRs. 

The first return is detected using the algorithm C_t = P_t * dP_t-1/dt, where P_t is the power at time frame t, and dP_t-1/dt is essentially the slope (gradient) along a given trace. This algorithm was adapted from Grima et al., 2012.

The max of this weighting criteria for each trace should correspond to the first return due to the highest energy at the surface, and the greatest leading edge due to the high dielectric contrast. In these scripts, to avoid high energy noise at the beginning of each trace, a delay of 100 pixels is implemented.

