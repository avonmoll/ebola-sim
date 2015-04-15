# Ebola Simulation

import numpy as np
#import shared
import csv
import heapq
import RNG
 
countries = []
Now = 0
PASSENGERS = 130    # roughly 737 size
THRESHOLD = 1000    # number of infected before travel reduction happens
REDUCTION_0 = 1.2   # initial travel reduction factor that will be applied to mean period for inbound/outbound routes
REDUCTION_SLOPE = 0 # REDUCTION_FACTOR = REDUCTION_0 + REDUCTION_SLOPE * (len(country.I) - THRESHOLD)

class State:
    S, E, I, H, F, R = range(6)
           
class Country(object):
    def __init__(self, name, code, pop, s_e, e_i, i_h, i_f, i_r, h_f, h_r, f_r, I0):
        self.name = name
        self.code = code
        self.population = pop
        
        # State Transition Rates
        self.s_e = s_e
        self.e_i = e_i
        self.i_h = i_h
        self.i_f = i_f
        self.i_r = i_r
        self.h_f = h_f
        self.h_r = h_r
        self.f_r = f_r
        
        # Containers for compartmentalized model of population
        self.S = pop
        self.E = []
        self.I = []
        self.H = []
        self.F = []
        self.R = []
        
        # Seed initial infected (I) population
        if I0 > 0:
            self.S = self.S - I0
            self.I = [Person(location = self, state = State.I) for p in range(I0)]
            
    def Update_Disease_Model(self):
        """Recalculate state transition parameters based on current population makeup
        
        No return value
        """
        raise NotImplementedError
        
    def Travel_Reduction(self):
        if len(self.I) > THRESHOLD:
            reduction_factor = REDUCTION_0 + REDUCTION_SLOPE * (len(self.I) - THRESHOLD)
            return reduction_factor
        else:
            return None
        
class Person(object):
    def __init__(self, location, state = State.E):
        """Instantiate a Person object when there is a transition from S->E (default)
        
        Keyword arguments:
        location -- a country object indicating the country this person occupies
        state    -- a State object corresponding to one of {S,E,I,F,H,R} indicating
                    the disease state of the individual
                    
        In general, only individuals in states other than S will be instantiated,
        lest the memory get out of control.
        """
        self.location = location
        self.state = state
        
class Flight_Generator(object):
    flightq = []
    routes = []
    
    @classmethod
    def Initialize(cls):
        cls.flightq = []
        cls.routes = []
        with open('relavant_routes.csv') as csvfile:
            csvreader = csv.reader(csvfile,delimiter=',')
            for row in csvreader:
                source = [c for c in countries if c.name == row[-3]][0]
                dest = [c for c in countries if c.name == row[-2]][0]
                T = row[-1]
                routes.append(Route(source,dest,T))                

    @classmethod
    def Schedule_Flight(cls, time, orig, dest, size):
        heapq.heappush(cls.flightq, (time, orig, dest, size))

    @classmethod
    def Reduce(cls, country, factor):
        affected_routes = [r for r in cls.routes if r.source == country or r.dest == country]
        for r in affected_routes:
            r.T = factor*r.T
    
    @classmethod
    def Execute_Todays_Flights(cls):
        while(cls.flightq[0][0] == Now):
            flight = heapq.heappop(cls.flightq)
            
            #TODO : select individuals at random from the S & E populations
            #TODO : update these individuals' location with the destination
            #TODO : remove them from origin population list and add to destination population list
        
class Route(object):
    def __init__(self, source, dest, mean_period):
        self.source = source
        self.dest = dest
        self.T = mean_period
    
    def Schedule_Next(self):
        global Now
        delta_t = np.round(RNG.Exponential(self.T))
        Flight_Generator.Schedule_Flight(Now+delta_t, self.source, self.dest, PASSENGERS)

def run(maxDays = 365):
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
    Flight_Generator.Initialize()        