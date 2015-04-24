# Entities

import settings
import RNG
import heapq
import numpy as np
import csv

class State:
    S, E, I, H, F, R = range(6)
           
class Country(object):
    def __init__(self, name, code, pop, incubation_period, symptoms_to_hospital, symptoms_to_death, hospital_to_death, infectious_period, hospital_to_noninfectious, death_to_burial, beta_i, beta_h, beta_f, percent_hospitalized, fatality_rate, I0):
        self.name = name
        self.code = code
        self.pop = int(pop)
        
        # State Parameters
        self.incubation_period = float(incubation_period)
        self.symptoms_to_hospital = float(symptoms_to_hospital)
        self.symptoms_to_death = float(symptoms_to_death)
        self.hospital_to_death = float(hospital_to_death)
        self.infectious_period = float(infectious_period)
        self.hospital_to_noninfectious = float(hospital_to_noninfectious)
        self.death_to_burial = float(death_to_burial)
        self.beta_i = float(beta_i)
        self.beta_h = float(beta_h)
        self.beta_f = float(beta_f)
        self.percent_hospitalized = float(percent_hospitalized)
        self.fatality_rate = float(fatality_rate)
        
        # Containers for compartmentalized model of population
        self.S = self.pop
        self.E = 0
        self.I = 0
        self.H = 0
        self.F = 0
        self.R = 0
        
        # Seed initial infected (I) population
        if (self.name in settings.I0) and (settings.I0[self.name] > 0):
            I0 = settings.I0[self.name]
            self.S = self.S - I0
            self.E = self.E + I0
        
        # Timeseries history of population makeup
        self.S_history = [self.S]
        self.E_history = [self.E]
        self.I_history = [self.I]
        self.H_history = [self.H]
        self.F_history = [self.F]
        self.R_history = [self.R]
        self.onset_history = [0]
        self.death_history = [0]
        self.cases = 0
        self.deaths = 0
        
        # Travel Factor
        self.travel_factor = 1
        
        # Initialize transition parameters
        self.Update_Disease_Model()
            
    def Update_Disease_Model(self):
        """Recalculate state transition parameters based on current population makeup
        
        No return value
        """
        self.s_e = (self.beta_i * self.S * self.I + self.beta_h * self.S * self.H + self.beta_f * self.S * self.F)/self.pop
        self.e_i = self.E * (1/self.incubation_period)
        self.i_h = self.percent_hospitalized * self.I * (1/self.symptoms_to_hospital)
        self.h_f = self.fatality_rate * self.H * (1/self.hospital_to_death)
        # print self.fatality_rate, self.H, self.hospital_to_death, self.h_f
        self.f_r = self.F * (1/self.death_to_burial)
        self.i_r = (1-self.percent_hospitalized) * (1-self.fatality_rate) * self.I * (1/self.infectious_period)
        self.i_f = (1-self.percent_hospitalized) * self.fatality_rate * self.I * (1/self.symptoms_to_death)
        self.h_r = (1-self.fatality_rate) * self.H * (1/self.hospital_to_noninfectious)

    def Disease_Transition(self):
        # S->E
        n = np.random.poisson(self.s_e)
        n = n if n <= self.S else self.S
        self.S = self.S - n
        self.E = self.E + n
        
        # E->I
        n = np.random.poisson(self.e_i)
        n = n if n <= self.E else self.E
        self.E = self.E - n
        self.I = self.I + n
        
        # I->H
        n = np.random.poisson(self.i_h)
        n = n if n <= self.I else self.I
        self.I = self.I - n
        self.H = self.H + n
        
        # I->F
        n = np.random.poisson(self.i_f)
        n = n if n <= self.I else self.I
        self.I = self.I - n
        self.F = self.F + n
        self.pop = self.pop - n
        
        # I->R
        n = np.random.poisson(self.i_r)
        n = n if n <= self.I else self.I
        self.I = self.I - n
        self.R = self.R + n
        
        # H->F
        n = np.random.poisson(self.h_f)
        n = n if n <= self.H else self.H
        self.H = self.H - n
        self.F = self.F + n
        self.pop = self.pop - n
                
        # H->R
        n = np.random.poisson(self.h_r)
        n = n if n <= self.H else self.H
        self.H = self.H - n
        self.R = self.R + n
        
        # F->R
        n = np.random.poisson(self.f_r)
        n = n if n <= self.F else self.F
        self.F = self.F - n
        self.R = self.R + n    
        
# class Person(object):
#     def __init__(self, location, state = State.E):
#         """Instantiate a Person object when there is a transition from S->E (default)
        
#         Keyword arguments:
#         location -- a country object indicating the country this person occupies
#         state    -- a State object corresponding to one of {S,E,I,F,H,R} indicating
#                     the disease state of the individual
                    
#         In general, only individuals in states other than S will be instantiated,
#         lest the memory get out of control.
#         """
#         self.location = location
#         self.state = state
        
class Flight_Generator(object):
    flightq = []
    routes = []
    
    @classmethod
    def Initialize(cls, countries):
        cls.flightq = []
        cls.routes = []
        with open('relevant_routes.csv') as csvfile:
            csvreader = csv.reader(csvfile,delimiter=',')
            csvreader.next()
            for row in csvreader:
                try:
                    orig = [c for c in countries if c.name == row[-5]][0]
                    dest = [c for c in countries if c.name == row[-4]][0]
                    T = float(row[-3])
                    T_std = float(row[-2])
                    seats = int(row[-1])
                    cls.routes.append(Route(orig,dest,T,T_std,seats))
                    cls.routes[-1].Schedule_Next(0)                
                except IndexError as e:
                    pass

    @classmethod
    def Schedule_Flight(cls, time, route):
        heapq.heappush(cls.flightq, (time, route))
    
    @classmethod
    def Execute_Todays_Flights(cls, Now):
        while(cls.flightq[0][0] == Now):
            _, flight = heapq.heappop(cls.flightq)
            
            #select individuals at random from the S & E populations
            poisson_lambda=float(flight.orig.E)/float(flight.orig.E+flight.orig.S)
            s=np.sum(np.random.poisson(poisson_lambda, flight.seats))

            #remove them from origin population list and add to destination population list
            if s > 0:
                s = flight.orig.E if s > flight.orig.E else s
                flight.orig.E=flight.orig.E - s
                flight.dest.E=flight.dest.E + s
     
            flight.orig.S=flight.orig.S - (flight.seats - s)
            flight.dest.S=flight.dest.S + (flight.seats - s)
            flight.orig.pop = flight.orig.pop - flight.seats
            flight.dest.pop = flight.dest.pop + flight.seats
            
            #schedule next flight
            flight.Schedule_Next(Now)
        
class Route(object):
    def __init__(self, orig, dest, mean_period, std_period, seats):
        self.orig = orig
        self.dest = dest
        self.T = mean_period
        self.T_std = std_period
        self.seats = seats
    
    def Schedule_Next(self,Now):
        tf = max([self.orig.travel_factor, self.dest.travel_factor])
        #delta_t = int(abs(round(RNG.Normal(self.T*tf, self.T_std), 0)))
        delta_t = np.random.poisson(self.T*tf)
        Flight_Generator.Schedule_Flight(Now+delta_t, self)
