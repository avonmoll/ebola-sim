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
        self.E = []
        self.I = []
        self.H = []
        self.F = []
        self.R = []
        
        # Seed initial infected (I) population
        if (self.name in settings.I0) and (settings.I0[self.name] > 0):
            I0 = settings.I0[self.name]
            self.S = self.S - settings.I0[self.name]
            self.I = [Person(location = self, state = State.I) for p in range(I0)]
        
        # Timeseries history of population makeup
        self.S_history = [self.S]
        self.E_history = [len(self.E)]
        self.I_history = [len(self.I)]
        self.H_history = [len(self.H)]
        self.F_history = [len(self.F)]
        self.R_history = [len(self.R)]
        self.onset_history = [0]
        self.death_history = [0]
        
        # Travel Factor
        self.travel_factor = 1
        
        # Initialize transition parameters
        self.Update_Disease_Model()
            
    def Update_Disease_Model(self):
        """Recalculate state transition parameters based on current population makeup
        
        No return value
        """
        self.s_e = (self.beta_i * self.S * len(self.I) + self.beta_h * self.S * len(self.H) + self.beta_f * self.S * len(self.F))/self.pop
        self.e_i = len(self.E) * (1/self.incubation_period)
        self.i_h = self.percent_hospitalized * len(self.I) * (1/self.symptoms_to_hospital)
        self.h_f = self.fatality_rate * len(self.H) * (1/self.hospital_to_death)
        self.f_r = len(self.F) * (1/self.death_to_burial)
        self.i_r = (1-self.percent_hospitalized) * (1-self.fatality_rate) * len(self.I) * (1/self.infectious_period)
        self.i_f = (1-self.percent_hospitalized) * self.fatality_rate * len(self.I) * (1/self.symptoms_to_death)
        self.h_r = (1-self.fatality_rate) * len(self.H) * (1/self.hospital_to_noninfectious)

    def Disease_Transition(self):
        # S->E
        n = np.random.poisson(self.s_e)
        E_new = [Person(self, State.E) for p in range(n)]
        self.E.extend(E_new)
        self.S = self.S - n
        
        # E->I
        n = np.random.poisson(self.e_i)
        I_new = self.E[:n]
        self.E = self.E[n:]
        for p in I_new:
            p.state = State.E
        self.I.extend(I_new)
        self.onset_history.append(n)
        
        # I->H
        n = np.random.poisson(self.i_h)
        H_new = self.I[:n]
        self.I = self.I[n:]
        for p in H_new:
            p.state = State.H
        self.H.extend(H_new)
        
        # I->F
        n = np.random.poisson(self.i_f)
        F_new = self.I[:n]
        self.I = self.I[n:]
        for p in F_new:
            p.state = State.F
        self.F.extend(F_new)
        self.death_history.append(n)
        self.pop = self.pop - n
        
        # I->R
        n = np.random.poisson(self.i_r)
        R_new = self.I[:n]
        self.I = self.I[n:]
        for p in R_new:
            p.state = State.R
        self.R.extend(R_new)
        
        # H->F
        n = np.random.poisson(self.h_f)
        F_new = self.H[:n]
        self.H = self.H[n:]
        for p in F_new:
            p.state = State.R
        self.F.extend(F_new)
        self.death_history[-1] = self.death_history[-1] + n
        self.pop = self.pop - n
                
        # H->R
        n = np.random.poisson(self.h_r)
        R_new = self.H[:n]
        self.H = self.H[n:]
        for p in R_new:
            p.state = State.R
        self.R.extend(R_new)
        
        # F->R
        n = np.random.poisson(self.f_r)
        R_new = self.F[:n]
        self.F = self.F[n:]
        for p in R_new:
            p.state = State.R
        self.R.extend(R_new)       
        
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
    def Execute_Todays_Flights(cls, Now):
        while(cls.flightq[0][0] == Now):
            _, flight = heapq.heappop(cls.flightq)
            
            #select individuals at random from the S & E populations
            poisson_lambda=float(len(flight.orig.E))/float(len(flight.orig.E)+flight.orig.S)
            s=np.sum(np.random.poisson(poisson_lambda, flight.seats))

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
