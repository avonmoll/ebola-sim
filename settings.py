# Settings

THRESHOLD = 1000                                                                # number of infected before travel reduction happens
REDUCTION_0 = 2.0                                                               # initial travel reduction factor that will be applied to mean period for inbound/outbound routes
REDUCTION_SLOPE = 0                                                             # REDUCTION_FACTOR = REDUCTION_0 + REDUCTION_SLOPE * (len(country.I) - THRESHOLD)
maxIter = 365                                                                   # days
I0 = {'Guinea':10}                                                              # initial infection seed