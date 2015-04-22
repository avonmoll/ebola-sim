# Ebola Simulation

import settings
import csv
from entities import *
import numpy as np
 
countries = []
Now = 0

def iter():
    global Now    
    for co in countries:
        co.Disease_Transition()
        co.Update_Disease_Model()
        
        # Perform travel restrictions based on epidemic size
        if len(co.I) >= settings.THRESHOLD:
            co.travel_factor = settings.TF0 + settings.TF_SLOPE * (len(co.I) - settings.THRESHOLD)
            
        co.S_history.append(co.S)
        co.E_history.append(len(co.E))
        co.I_history.append(len(co.I))
        co.H_history.append(len(co.H))
        co.F_history.append(len(co.F))
        co.R_history.append(len(co.R))

    Flight_Generator.Execute_Todays_Flights(Now)
            
def initialize():
    global Now, countries
    Now = 0
    countries = []
    with open('country_data.csv','rb') as csvfile:
        country_reader = csv.reader(csvfile, delimiter=',')
        country_reader.next()
        for row in country_reader:
            countries.append(Country(*row))
    Flight_Generator.Initialize(countries)    
    
def output():
    import pandas as pd
    sim_history = pd.DataFrame(columns=('Country','S','E','I','H','F','R','OnsetCases','Deaths'))
    n_country = 0
    for co in countries:
        offset = settings.maxIter*n_country
        for i in range(settings.maxIter):
            sim_history.loc[offset+i] = [co.name, co.S_history[i], co.E_history[i], co.I_history[i], co.H_history[i], co.F_history[i], co.R_history[i], co.onset_history[i], deaths[i]]
        n_country = n_country + 1
    return sim_history