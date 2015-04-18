# Discrete Time Simulation Engine

def run(application):
    '''Runs the specified application until its maximum time
    
    application -- a Python module that completely specifies the application of
                   the simulation. The module must contain the following:
                       - settings: submodule containing an int called maxIter
                       - output(): function which returns any relevant outputs
                       - initialize(): function which performs any necessary
                                       setup
                       - Now: global variable for tracking current simulation
                              time
                       - iter(): a function which performs all necessary
                                 operations for each discrete time step
    '''
    
    application.initialize()
    for i in application.settings.maxIter:
        application.iter()
        application.Now += 1
    return application.output()