# Settings
import numpy as np     
                                                         
THRESHHOLD_MIN=100
THRESHHOLD_MAX=200
THRESHHOLD_INCREMENT=100
THRESHHOLD_MAX=THRESHHOLD_MAX+THRESHHOLD_INCREMENT
THRESHHOLD_RANGE=np.arange(THRESHHOLD_MIN,THRESHHOLD_MAX,THRESHHOLD_INCREMENT)  # number of infected before travel reduction happens

                                                                       
TF0_MIN=1
TF0_MAX=2
TF0_INCREMENT=1
TF0_MAX=TF0_MAX+TF0_INCREMENT
TF0_RANGE=np.arange(TF0_MIN,TF0_MAX,TF0_INCREMENT)                              # initial travel reduction factor that will be applied to mean period for inbound/outbound routes

TF_SLOPE = 0                                                                    # TF = TF0 + TF_SLOPE * (len(country.I) - THRESHOLD)
maxIter = 365                                                                   # days
I0 = {'Guinea':10}                                                              # initial infection seed