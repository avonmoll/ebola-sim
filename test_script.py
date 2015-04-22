# test script

import ebola_sim
reload(ebola_sim)

import discrete_time_engine as engine
reload(engine)

import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
#import pprofile

def main():
    # TODO : mess with settings
    ebola_sim.settings.maxIter = 180
    ebola_sim.settings.I0['Guinea'] = 50
    
    results = []
    
    #profiler = pprofile.Profile()
    
    #with profiler:
    for i in range(20):
        tic = time.clock()
        output = engine.run(ebola_sim)
        results.append(output)
        toc = time.clock()
        print '%02d Execution Time  -- %d:%02d mm:ss'%(i, int((toc-tic)/60),int((toc-tic)%60))
    #profiler.dump_stats('profile')
    aggregate(results)

def aggregate(res_list):
    countries = res_list[0]['Country']
    res = pd.concat((res_list.pop(),res_list.pop()))
    while len(res_list) > 0:
        pd.concat((res,res_list.pop()))
    by_row_index = res.groupby(res.index)
    res_ave = by_row_index.mean()
    res_ave.insert(0,'Country',countries)
    res_std = by_row_index.std()
    res_std.insert(0,'Country',countries)
    res_ave.to_csv('results_ave.csv')
    res_std.to_csv('results_std.csv')

def plot_results():
    res_ave = pd.read_csv('results_ave.csv', index_col = False)
    res_std = pd.read_csv('results_std.csv', index_col = False)
    
    ave_grouped = res_ave.groupby('Country')
    std_grouped = res_std.groupby('Country')
    
    for country, c_ave in ave_grouped:
        f, ax = plt.subplots(3,1,sharex=True)
        c_std = std_grouped.get_group(country)
        
        s_ave, s_std = np.array(c_ave['S']), np.array(c_std['S'])
        e_ave, e_std = np.array(c_ave['E']), np.array(c_std['E'])
        i_ave, i_std = np.array(c_ave['I']), np.array(c_std['I'])
        h_ave, h_std = np.array(c_ave['H']), np.array(c_std['H'])
        f_ave, f_std = np.array(c_ave['F']), np.array(c_std['F'])
        r_ave, r_std = np.array(c_ave['R']), np.array(c_std['R'])
        
        x = range(ebola_sim.settings.maxIter + 1)
        a = 0.2
        ax[0].plot(x, s_ave, 'b')
        tax = ax[0].twinx()
        tax.plot(x,e_ave, 'g', i_ave, 'r', h_ave, 'y', f_ave, 'k', r_ave, 'k--') 
        ax[0].fill_between(x, s_ave-s_std, s_ave+s_std, color = 'b', alpha=a)
        tax.fill_between(x, e_ave-e_std, e_ave+e_std, color = 'g', alpha=a)
        tax.fill_between(x, i_ave-i_std, i_ave+i_std, color = 'r', alpha=a)
        tax.fill_between(x, h_ave-h_std, h_ave+h_std, color = 'y', alpha=a)
        tax.fill_between(x, f_ave-f_std, f_ave+f_std, color = 'k', alpha=a)
        tax.fill_between(x, r_ave-r_std, r_ave+r_std, color = 'k', alpha=a)
        #tax.legend(['S','E','I','H','F','R'],bbox_to_anchor=(1.05,1),loc=2,borderaxespad=0.)
        ax[0].legend(['S'], loc = 3) 
        tax.legend(['E','I','H','F','R'],loc=2)
        tax.set_title(country.decode('utf-8'))
        ax[0].set_ylabel('S')
        tax.set_ylabel('E, I, H, F, R')
        
        o_ave, o_std = np.array(c_ave['OnsetCases']), np.array(c_std['OnsetCases'])
        d_ave, d_std = np.array(c_ave['Deaths']), np.array(c_std['Deaths'])
                
        ax[1].plot(x, o_ave, 'k')
        ax[1].fill_between(x, o_ave-o_std, o_ave+o_std, color = 'k', alpha=a)
        ax[1].set_ylabel('Cases per day')
        
        ax[2].plot(x, d_ave, 'k')
        ax[2].fill_between(x, d_ave-d_std, d_ave+d_std, color = 'k', alpha=a)
        ax[2].set_ylabel('Deaths per day')
        ax[2].set_xlabel('Day')
        
        plt.tight_layout()
    plt.show()

if __name__=='__main__':
    main()
    plot_results()