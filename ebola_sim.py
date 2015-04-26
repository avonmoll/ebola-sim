# Ebola Simulation

import settings
import csv
from entities import *
import pandas as pd
 
countries = []
Now = 0

def iter():
    global Now    
    for co in countries:
        co.Disease_Transition()
        co.Update_Disease_Model()
        
        # Perform travel restrictions based on epidemic size
        if co.I >= settings.THRESHOLD:
            co.travel_factor = settings.TF0 + settings.TF_SLOPE * (co.I - settings.THRESHOLD)

        co.S_history.append(co.S)
        co.E_history.append(co.E)
        co.I_history.append(co.I)
        co.H_history.append(co.H)
        co.F_history.append(co.F)
        co.R_history.append(co.R)
        co.onset_history.append(co.cases)
        co.death_history.append(co.deaths)

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
    col = ('Country','S','E','I','H','F','R','OnsetCases','Deaths')
    sim_history = pd.DataFrame(columns=col)
    #n_country = 0
    for co in countries:
        #offset = settings.maxIter*n_country
        #for i in range(settings.maxIter):
        #    sim_history.loc[offset+i] = [co.name, co.S_history[i], co.E_history[i], co.I_history[i], co.H_history[i], co.F_history[i], co.R_history[i], co.onset_history[i], co.death_history[i]]
        #n_country = n_country + 1
        data = {'Country':[co.name]*(settings.maxIter+1), 'S':co.S_history, 'E':co.E_history, 'I':co.I_history, 'H':co.H_history, 'F':co.F_history, 'R':co.R_history, 'OnsetCases':co.onset_history, 'Deaths':co.death_history}
        co_history = pd.DataFrame.from_dict(data)
        sim_history = pd.concat((sim_history,co_history),ignore_index=True)
    return sim_history