import numpy as np

x = 19 #initialize seed for first call

def Random():
    #suggested values for Lehmer (Lemmis/Park)
    global x
    m = np.power(2,31)-1 #modulus value = 2,147,483,647
    a = 48271 #multiplier
    q = 44488
    r = 3399
    #if new_seed: #use truthiness to check if last_seed exists & != 0
    #    x = new_seed
    #Lehmer algorithm to compute ax mod m without overflow
    t = a*(x % q) - r*(x / q)
    if (t > 0):
        x = t 
    else:
        x = t + m 
    return x / float(m) #normalize ~ (0,1)

#Generate Random Variates for Simulation
def Exponential(scale): 
    u = Random() # generate random number between (0,1) 
    #rv = expon.ppf(u, scale=scale)
    rv = -np.log(1-u)/scale
    return rv
    
#Sample from Poisson distribution 
def Poisson(scale, n = 1):
    """Take n samples from Poisson distribution whose mean = scale
    
    Based on inverse transform sampling (Devroye, Luc (1986). "Discrete 
    Univariate Distributions". Non-Uniform Random Variate Generation. New York: 
    Springer-Verlag. p. 505)
    """
    x = np.zeros(n)
    for i in range(n):
        u = Random()
        p = np.exp(-scale)
        s = p
        while u > s:
            x[i] = x[i] + 1
            p = p*scale/x[i]
            s = s + p
    if len(x) == 1:
        return x[0]
    else:
        return x
        
# Sample from Normal distribution
def Normal(mean, std):
    #TODO : write our own version of this if possible!
    return np.normal(mean,std)