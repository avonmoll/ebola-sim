# Settings

THRESHOLD = 1000                                                                # number of infected before travel reduction happens
TF0 = 2.0                                                                       # initial travel reduction factor that will be applied to mean period for inbound/outbound routes
TF_SLOPE = 0                                                                    # TF = TF0 + TF_SLOPE * (len(country.I) - THRESHOLD)
maxIter = 365                                                                   # days
I0 = {'Guinea':10}                                                              # initial infection seed