# Ebola Simulation

import settings
import csv
from entities import *
 
countries = []
Now = 0

def iter():
    global Now
    for day in range(maxDays):
        Flight_Generator.Execute_Todays_Flights()    
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
        Now = Now + 1
            
def initialize():
    global Now
    Now = 0
    countries = []
    with open('country_data.csv','rb') as csvfile:
        country_reader = csv.reader(csvfile, delimiter=',')
        for row in country_reader:
            countries.append(Country(*row))
    Flight_Generator.Initialize(countries)    
    
def output():
    raise NotImplementedError  