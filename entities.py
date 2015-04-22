# Entities

import settings
import RNG
import heapq
import numpy as np
import csv
import random

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
        self.E = []
        self.I = []
        self.H = []
        self.F = []
        self.R = []
        
        # Seed initial infected (I) population
        if I0 > 0:
            self.S = self.S - I0
            self.I = [Person(location = self, state = State.I) for p in range(I0)]

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
        self.f_r = self.F * (1/self.death_to_burial)
        self.i_r = (1-self.percent_hospitalized) * (1-self.fatality_rate) * self.I * (1/self.infectious_period)
        self.i_f = (1-self.percent_hospitalized) * self.fatality_rate * self.I * (1/self.symptoms_to_death)
        self.h_r = (1-self.fatality_rate) * self.H * (1/self.hospital_to_noninfectious)
        
    def Travel_Reduction(self):
        if len(self.I) > settings.THRESHOLD:
            reduction_factor = settings.REDUCTION_0 + settings.REDUCTION_SLOPE * (len(self.I) - settings.THRESHOLD)
            return reduction_factor
        else:
            return None

   def Disease_Transition(self):
        transition_rates=[self.s_e,self.e_i,self.i_h,self.i_f,self.i_r,self.h_f,self.h_r,self.f_r]
        pop_list=[self.S,self.E,self.I,self.H,self.F,self.R]
        states=[S,E,I,H,F,R]
        for r in range(0,len(transition_rates)):
            if r < 2:
                n = RNG.Poisson(transition_rates[r]) # number of people to transition
                temp = pop_list[r][:n]
                del pop_list[r][0:n]
                for p in temp:
                    p.state=states[r+1]
                    pop_list[r+1].append(p)
            elif r < 5:
                n = RNG.Poisson(transition_rates[r]) # number of people to transition
                temp = pop_list[2][:n]
                del pop_list[2][0:n]
                for p in temp:
                    p.state=states[r+1]
                    pop_list[r+1].append(p)
            elif r < 7:
                n = RNG.Poisson(transition_rates[r]) # number of people to transition
                temp = pop_list[3][:n]
                del pop_list[3][0:n]
                for p in temp:
                    p.state=states[r-1]
                    pop_list[r-1].append(p)
            else:
                n = RNG.Poisson(transition_rates[r]) # number of people to transition
                temp = pop_list[4][:n]
                del pop_list[4][0:n]
                for p in temp:
                    p.state=states[r-2]
                    pop_list[r-2].append(p)
                    
        
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
        with open('relevant_routes.csv') as csvfile:
            csvreader = csv.reader(csvfile,delimiter=',')
            csvreader.next()
            for row in csvreader:
                orig = [c for c in countries if c.name == row[-5]][0]
                dest = [c for c in countries if c.name == row[-4]][0]
                T = float(row[-3])
                T_std = float(row[-2])
                seats = int(row[-1])
                cls.routes.append(Route(orig,dest,T,T_std,seats))
                cls.routes[-1].Schedule_Next(0)                

    @classmethod
    def Schedule_Flight(cls, time, route):
        heapq.heappush(cls.flightq, (time, route))

    @classmethod
    def Reduce(cls, country, factor):
        affected_routes = [r for r in cls.routes if r.orig == country or r.dest == country]
        for r in affected_routes:
            r.T = factor*r.T
    
    @classmethod
    def Execute_Todays_Flights(cls, Now):
        while(cls.flightq[0][0] == Now):
            _, flight = heapq.heappop(cls.flightq)
            
            #select individuals at random from the S & E populations
            poisson_lambda=float(len(flight.orig.E))/float(len(flight.orig.E)+flight.orig.S)
            s=np.sum(RNG.Poisson(poisson_lambda, flight.seats))

            #remove them from origin population list and add to destination population list
            if s > 0:
                s = len(flight.orig.E) if s > len(flight.orig.E) else s
                np.random.shuffle(flight.orig.E)
                exposed_transfer=flight.orig.E[:s]
                flight.orig.E = flight.orig.E[s:]
            
                # TODO : make the selection from I population random such as:
                #         infected_transfer = [flight.orig.I[i] for i in sorted(np.random.sample(xrange(len(flight.orig.I)),s))]
            
                flight.dest.E.extend(exposed_transfer)
     
                #update these individuals' location with the destination
                for individual in exposed_transfer:
                    individual.location = flight.dest
     
            flight.orig.S=flight.orig.S - (flight.seats - s)
            flight.dest.S=flight.orig.S + (flight.seats - s)
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
        delta_t = int(abs(round(RNG.Normal(self.T, self.T_std), 0))
        Flight_Generator.Schedule_Flight(Now+delta_t, self)
