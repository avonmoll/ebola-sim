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
        # TODO : Draw transitions from Poisson for every transition
        # TODO : Choose people randomly and change state

        co.Update_Disease_Model()
        travel_reduction = co.Travel_Reduction()
        if travel_reduction != None:
            Flight_Generator.Reduce(co, travel_reduction)
        
        # TODO : aggregate statistics we need (# dead, # onset cases this day, etc.)    
        #        These stats could be bound to the country class instances or just put in
        #        some general containers        
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
        # TODO : remove the following 2 lines once state transitions are properly handled
        onset = [0]*settings.maxIter
        deaths = [0]*settings.maxIter
        offset = settings.maxIter*n_country
        for i in range(settings.maxIter):
            sim_history.loc[offset+i] = [co.name, co.S_history[i], co.E_history[i], co.I_history[i], co.H_history[i], co.F_history[i], co.R_history[i], onset[i], deaths[i]]
        n_country = n_country + 1
    return sim_history