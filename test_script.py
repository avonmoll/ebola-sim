# test script

import ebola_sim
reload(ebola_sim)

import discrete_time_engine as engine
reload(engine)

import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t as student_t
#import pprofile

THRESHOLD_MIN=100
THRESHOLD_MAX=1000
THRESHOLD_RANGE=np.linspace(THRESHOLD_MIN,THRESHOLD_MAX,3)  
                                                                       
TF0_MIN=1.5
TF0_MAX=4
TF0_RANGE=np.linspace(TF0_MIN,TF0_MAX,3)                              

THRESHOLD_setting=[]
TF0_setting=[]

n = 5 # how many times to aggregate

def main():
    # TODO : mess with settings
    ebola_sim.settings.maxIter = 180
    ebola_sim.settings.I0['Guinea'] = 50
    
    results = []
    
    #profiler = pprofile.Profile()
    
    #with profiler:
    for threshold in THRESHOLD_RANGE:
        for TF0 in TF0_RANGE:
            ebola_sim.settings.THRESHOLD = threshold
            ebola_sim.settings.TF0 = TF0
            for i in range(n):
                tic = time.clock()
                output = engine.run(ebola_sim)
                results.append(output)
                toc = time.clock()
                print '%02d Execution Time  -- %d:%02d mm:ss'%(i, int((toc-tic)/60),int((toc-tic)%60))
            aggregate(results, 'results/%s_%s_%s_%s'%(str(int(threshold)),str(int(TF0*100)),str(ebola_sim.settings.maxIter),str(n)))
    #profiler.dump_stats('profile')

def aggregate(res_list, filename):
    countries = res_list[0]['Country']
    res = pd.concat((res_list.pop(),res_list.pop()))
    while len(res_list) > 0:
        pd.concat((res,res_list.pop()))
    by_row_index = res.groupby(res.index)
    res_ave = by_row_index.mean()
    res_ave.insert(0,'Country',countries)
    res_std = by_row_index.std()
    res_std.insert(0,'Country',countries)
    res_ave.to_csv('%s_ave.csv'%(filename))
    res_std.to_csv('%s_std.csv'%(filename))

def plot_results(filestub):
    '''Plots all countries data contained in the files corresponding to filestub
    
    For example, if filestub = 'results/100_200_180_5' this corresponds to results
    where THRESHOLD = 100 and TF0 = 2.00 and settings.maxIter = 180 and  n = 5
    '''
    def lower_and_upper(means, stds, n):
        lower, upper = [0]*len(means), [0]*len(means)
        for i in range(len(means)):
            m = means[i]
            s = stds[i]
            lower[i], upper[i] = student_t.interval(0.95, n, loc = m, scale = s)
            
        return lower, upper
    
    res_ave = pd.read_csv('%s_ave.csv'%(filestub), index_col = False)
    res_std = pd.read_csv('%s_std.csv'%(filestub), index_col = False)
    
    ave_grouped = res_ave.groupby('Country')
    std_grouped = res_std.groupby('Country')
    
    n = int(filestub.rpartition('_')[-1])
    days = int(filestub.rpartition('_')[0].rpartition('_')[-1])
    
    for country, c_ave in ave_grouped:
        f, ax = plt.subplots(3,1,sharex=True)
        c_std = std_grouped.get_group(country)
        
        s_ave, s_std = np.array(c_ave['S']), np.array(c_std['S'])
        e_ave, e_std = np.array(c_ave['E']), np.array(c_std['E'])
        i_ave, i_std = np.array(c_ave['I']), np.array(c_std['I'])
        h_ave, h_std = np.array(c_ave['H']), np.array(c_std['H'])
        f_ave, f_std = np.array(c_ave['F']), np.array(c_std['F'])
        r_ave, r_std = np.array(c_ave['R']), np.array(c_std['R'])
        
        s_l, s_u = lower_and_upper(s_ave,s_std, n)
        e_l, e_u = lower_and_upper(e_ave,e_std, n)
        i_l, i_u = lower_and_upper(i_ave,i_std, n)
        h_l, h_u = lower_and_upper(h_ave,h_std, n)
        f_l, f_u = lower_and_upper(f_ave,f_std, n)
        r_l, r_u = lower_and_upper(r_ave,r_std, n)
        
        x = range(days + 1)
        a = 0.2
        h1, = ax[0].plot(x, s_ave, 'b')
        tax = ax[0].twinx()
        h2, h3, h4, h5, h6, = tax.plot(x,e_ave, 'g', i_ave, 'r', h_ave, 'y', f_ave, 'k', r_ave, 'k--') 
        ax[0].fill_between(x, s_u, s_l, color = 'b', alpha=a)
        tax.fill_between(x, e_u, e_l, color = 'g', alpha=a)
        tax.fill_between(x, i_u, i_l, color = 'r', alpha=a)
        tax.fill_between(x, h_u, h_l, color = 'y', alpha=a)
        tax.fill_between(x, f_u, f_l, color = 'k', alpha=a)
        tax.fill_between(x, r_u, r_l, color = 'k', alpha=a)
        #tax.legend(['S','E','I','H','F','R'],bbox_to_anchor=(1.05,1),loc=2,borderaxespad=0.)
        #ax[0].legend(['S'], loc = 3) 
        tax.legend([h1,h2,h3,h4,h5,h6],['S','E','I','H','F','R'],loc=2)
        tax.set_title(country.decode('utf-8'))
        ax[0].set_ylabel('S')
        tax.set_ylabel('E, I, H, F, R')
        tax.set_ylim([0,int(max(e_ave + i_ave + h_ave + f_ave + r_ave))+1])
        
        o_ave, o_std = np.array(c_ave['OnsetCases']), np.array(c_std['OnsetCases'])
        d_ave, d_std = np.array(c_ave['Deaths']), np.array(c_std['Deaths'])
        o_l, o_u = lower_and_upper(o_ave, o_std, n)
        d_l, d_u = lower_and_upper(d_ave, d_std, n)
        
        cum_o = np.cumsum(o_ave)
        cum_d = np.cumsum(d_ave)
                
        h1, = ax[1].plot(x, o_ave, 'k')
        ax[1].fill_between(x, o_l, o_u, color = 'k', alpha=a)
        tax1 = ax[1].twinx()
        h2, = tax1.plot(x, cum_o, 'r')
        tax1.set_ylabel('Cumulative')
        ax[1].set_ylabel('Cases per day')
        tax1.legend([h1,h2],['Per Day','Cum.'],loc=2)
        ax[1].set_ylim([0,max(o_ave)+1])
        tax1.set_ylim([0,max(cum_o)+1])
        
        h1, = ax[2].plot(x, d_ave, 'k')
        ax[2].fill_between(x, d_l, d_u, color = 'k', alpha=a)
        tax2 = ax[2].twinx()
        h2, = tax2.plot(x, cum_d, 'r')
        tax2.set_ylabel('Cumulative')
        tax2.legend([h1,h2],['Per Day','Cum.'], loc=2)
        ax[2].set_ylabel('Deaths per day')
        ax[2].set_xlabel('Day')
        ax[2].set_ylim([0,max(d_ave)+1])
        tax2.set_ylim([0,max(cum_d)+1])
        
        plt.tight_layout()
    plt.show()


if __name__=='__main__':
    main()