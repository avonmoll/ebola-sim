# Ebola Simulation

#import numpy as np
#import shared
import csv
import heapq
 
countries = []
Now = 0

class State:
    S, E, I, H, F, R = range(6)
           
class Country(object):
    def __init__(self, name, pop, s_e, e_i, i_h, i_f, i_r, h_f, h_r, f_r, I0):
        self.name = name
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
    
    @classmethod
    def Initialize(cls):
        cls.flightq = []

    @classmethod
    def Schedule_Flight(cls, time, orig, dest, size):
        heapq.heappush(cls.flightq, (time, orig, dest, size))

    @classmethod
    def Execute_Todays_Flights(cls):
        while(cls.flightq[0][0] == Now):
            flight = heapq.heappop(cls.flightq)
            
            #TODO : select individuals at random from the S & E populations
            #TODO : update these individuals' location with the destination
            #TODO : remove them from origin population list and add to destination population list
        


def run(maxDays = 365):
    global Now
    for day in range(maxDays):
        Flight_Generator.Execute_Todays_Flights()    
        for co in countries:
            # TODO : Draw transitions from Poisson for every transition
            # TODO : Choose people randomly and change state

            co.Update_Disease_Model()
            
            # TODO : aggregate statistics we need (# dead, # onset cases this day, etc.)    
            #        These stats could be bound to the country class instances or just put in
            #        some general containers        
        Now = Now + 1
            
def initialize():
    global Now
    Now = 0
    countries = []
    Flight_Generator.Initialize()
    with open('country_data.csv','rb') as csvfile:
        country_reader = csv.reader(csvfile, delimiter=',')
        for row in country_reader:
            countries.append(Country(*row))
        