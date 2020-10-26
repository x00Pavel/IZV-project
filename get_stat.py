import numpy as np
from operator import itemgetter
from pprint import pprint as pp
import matplotlib.pyplot as plt

REGIONS ={
    "PHA": ("00.csv", "Hlavní město Praha"),
    "STC": ("01.csv", "Středočeský"),
    "JHC": ("02.csv", "Jihočeský"),
    "PLK": ("03.csv", "Plzeňský"),
    "KVK": ("19.csv", "Karlovarský"), 
    "ULK": ("04.csv", "Ústecký"),
    "LBK": ("18.csv", "Liberecký"),
    "HKK": ("05.csv", "Královéhradecký"), 
    "PAK": ("17.csv", "Pardubický"),
    "OLK": ("14.csv", "Olomoucký"),
    "MSK": ("07.csv", "Moravskoslezský"), 
    "JHM": ("06.csv", "Jihomoravský"),
    "ZLK": ("15.csv", "Zlínský"),
    "VYS": ("16.csv", "Kraj Vysočina") 
}

def plot_stat(data_source, fig_location = None, show_figure = False):
    stats = {}
    regions = data_source[1][0]
    years = [i.split("-")[0] for i in np.datetime_as_string(data_source[1][3])]

    for index, year in enumerate(years):
        if year not in stats.keys():
            stats[year] = {}

        if regions[index] in stats[year].keys():
            stats[year][regions[index]] += 1
        else:
            stats[year][regions[index]] = 1

    fig, plots = plt.subplots(len(stats))
    fig.suptitle('My statistics')
    # plots.invert_yaxis() 

    for index, year in enumerate(stats.keys()):
        stats[year] =  sorted(stats[year].items(), key=itemgetter(1), reverse=True) # {k: v for k, v in sorted(stats[year].items(), key=lambda item: item[1])}
        # print(type(stats[year]))
        rects = plots[index].bar(range(len(stats[year])), [i[1] for i in stats[year]], align='center')
        plots[index].set_xticks(range(len(stats[year])))
        plots[index].set_xticklabels([i[0] for i in stats[year]])
        plots[index].title.set_text(f"Year {year}")
        for s in ['top', 'right']: 
            plots[index].spines[s].set_visible(False) 
        for rect in rects:
            height = rect.get_height()
            plots[index].text(rect.get_x() + rect.get_width()/2., 1.05*height,
                    '%d' % int(height),
                    ha='center', va='bottom')

    fig.tight_layout()
    plt.show()
    # pp(stats)
