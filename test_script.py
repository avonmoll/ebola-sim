# test script

import ebola_sim
reload(ebola_sim)

import discrete_time_engine as engine
import pandas as pd

# TODO : mess with settings
ebola_sim.settings.maxIter = 30

# TODO : aggregate data from multiple runs
output = engine.run(ebola_sim)
output.to_csv('results.csv', index = False)