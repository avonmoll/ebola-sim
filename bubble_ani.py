import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cartopy
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
import csv
import pandas as pd

fig, ax = plt.subplots(figsize=(30,30))

#line, = ax.plot(x, np.sin(x))

ebola_countries = []
with open('country_data.csv','rb') as csvfile:
    country_reader = csv.reader(csvfile, delimiter=',')
    country_reader.next()
    for row in country_reader:
        ebola_countries.append(row[1])

ax = plt.axes(projection=ccrs.PlateCarree())
#ax.add_feature(cartopy.feature.LAND)
ax.add_feature(cartopy.feature.OCEAN)
#ax.add_feature(cartopy.feature.COASTLINE)
#ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5)
#ax.add_feature(cartopy.feature.LAKES, alpha=0.95)
#ax.add_feature(cartopy.feature.RIVERS)
ax.set_extent(np.array([-125, 55, -10, 60]),ccrs.PlateCarree())

shpfilename = shpreader.natural_earth(resolution='110m',
                                      category='cultural',
                                      name='admin_0_countries')
reader = shpreader.Reader(shpfilename)
countries = reader.records()
countries = [c for c in countries]

bubbles = {}
for country in countries:
    if country.attributes['adm0_a3'] in ebola_countries:
        ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                          facecolor=(.9, .9, 1),
                          label=country.attributes['adm0_a3'])
        x = [np.mean([country.bounds[0],country.bounds[2]])]
        y = [np.mean([country.bounds[1],country.bounds[3]])]
        dot, = ax.plot(x,y, 'o', markersize=.1, color = 'r', alpha = .5,transform=ccrs.PlateCarree())
        if country.attributes['name']== "C\xf4te d'Ivoire":
            country.attributes['name'] = "C\xc3\xb4te d'Ivoire"
        bubbles[country.attributes['name']] = dot
    #else:
    #    ax.add_geometries(country.geometry, ccrs.PlateCarree(),
    #                      facecolor=(1, 1, 1),
    #                      label=country.attributes['adm0_a3'])

#ax.set_extent(np.array([-125, 55, 0, 20]))

def get_data(filestub):
    res_ave = pd.read_csv('%s_ave.csv'%(filestub), index_col = False)
    #res_std = pd.read_csv('%s_std.csv'%(filestub), index_col = False)
    ave_grouped = res_ave.groupby('Country')
    #std_grouped = res_std.groupby('Country')
    n = int(filestub.rpartition('_')[-1])
    days = int(filestub.rpartition('_')[0].rpartition('_')[-1])
    d = {}
    for country, c_ave in ave_grouped:
        #c_std = std_grouped.get_group(country)
        o_ave = np.array(c_ave['OnsetCases'])
        #d_ave, d_std = np.array(c_ave['Deaths'])
        cum_o = np.cumsum(o_ave)
        #cum_d = np.cumsum(d_ave)
        d[country] = cum_o
    return d, days
    
data = {}
maxDays = 0
data, maxDays = get_data('results/100_150_180_5')

msg = ax.text(-124, 0, ' ', fontsize=16)

def animate(i):
    global data, bubbles
    #ax.set_title('Day: %03d of %03d'%(i, maxDays),fontsize=16)
    msg.set_text('Day %03d of %03d'%(i, maxDays))
    #msg = ax.text(-124,0,'Day %03d of %03d'%(i, maxDays))
    dots = []
    dots.append(msg)
    for country in bubbles:
        cases = data[country][i]
        if cases > 1:
            sz = 40*np.log(cases)
        else:
            sz = 0
        sz = min(data[country][i],100)
        bubbles[country].set_markersize(sz)
        dots.append(bubbles[country])
    return dots

#Init only required for blitting to give a clean slate.
def init():
    #ax.set_title('Day: %03d of %03d'%(0, maxDays),fontsize=16)
    msg.set_text(' ')
    global data, bubbles
    dots = []
    dots.append(msg)
    for country in bubbles:
        bubbles[country].set_markersize(0.1)
        dots.append(bubbles[country])
    return dots

ani = animation.FuncAnimation(fig, animate, np.arange(0, maxDays), init_func=init,
    interval=75, blit=True)
    
ani.save('bubble_ani.mp4')

plt.show()