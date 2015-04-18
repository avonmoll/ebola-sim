# Entities

import settings
import RNG
import heapq
import numpy as np
import csv

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
        if len(self.I) > settings.THRESHOLD:
            reduction_factor = settings.REDUCTION_0 + settings.REDUCTION_SLOPE * (len(self.I) - settings.THRESHOLD)
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
    def Initialize(cls, countries):
        cls.flightq = []
        cls.routes = []
        with open('relavant_routes.csv') as csvfile:
            csvreader = csv.reader(csvfile,delimiter=',')
            for row in csvreader:
                orig = [c for c in countries if c.name == row[-5]][0]
                dest = [c for c in countries if c.name == row[-4]][0]
                T = row[-3]
                T_std = row[-2]
                seats = row[-1]
                cls.routes.append(Route(orig,dest,T,T_std,seats))                

    @classmethod
    def Schedule_Flight(cls, time, route):
        heapq.heappush(cls.flightq, (time, route))

    @classmethod
    def Reduce(cls, country, factor):
        affected_routes = [r for r in cls.routes if r.orig == country or r.dest == country]
        for r in affected_routes:
            r.T = factor*r.T
    
    @classmethod
    def Execute_Todays_Flights(cls):
        while(cls.flightq[0][0] == Now):
            flight = heapq.heappop(cls.flightq)
            
            #select individuals at random from the S & E populations
            poisson_lambda=float(len(flight.orig.E))/float(len(flight.orig.E)+flight.orig.S)
            s=np.sum(RNG.Poisson(poisson_lambda, flight.seats))

            #remove them from origin population list and add to destination population list
            # infected_transfer=flight.orig.I.pop(s)
            infected_transfer = [flight.orig.I[i] for i in sorted(np.random.sample(xrange(len(flight.orig.I)),s))]
            flight.dest.I.extend(infected_transfer)
            flight.orig.S=flight.orig.S - (flight.seats - s)
            flight.dest.S=flight.orig.S + (flight.seats - s)

            #update these individuals' location with the destination
            for individual in infected_transfer:
                individual.location = flight.dest

            #update the Disease model
            #flight[1].Update_Disease_Model()
            #flight[2].Update_Disease_Model()
            
            #schedule next flight
            flight.Schedule_Next()
        
class Route(object):
    def __init__(self, orig, dest, mean_period, std_period, seats):
        self.orig = orig
        self.dest = dest
        self.T = mean_period
        self.T_std = std_period
        self.seats = seats
    
    def Schedule_Next(self):
        global Now
        delta_t = abs(int(RNG.Normal(self.T, self.T_std)))
        Flight_Generator.Schedule_Flight(Now+delta_t, self)
