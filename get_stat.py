import numpy as np
from operator import itemgetter
from pprint import pprint as pp
import matplotlib.pyplot as plt
from os import path, mkdir
from argparse import ArgumentParser
from download import DataDownloader


def plot_stat(data_source, fig_location=None, show_figure=False):
    """Generete dinamical figure from given data set.

    Arguments:
    data_source -- tuple with two lists. First list containt names for each 
                   array in second list with numpy array data type.
    fig_location -- folder, where result figure should be stored (default None)
    show_figure -- define if result figure should be shown or not (default False)
    """
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

    fig, plots = plt.subplots(
        len(stats), figsize=[len(stats["2016"]) + 2, 10], sharey=True)
    fig.suptitle('Amount of car crashes in CR regions')
    values = []

    for index, year in enumerate(stats.keys()):
        stats[year] = sorted(stats[year].items(),
                             key=itemgetter(1), reverse=True)
        values += [i[1] for i in stats[year]]
        rects = plots[index].bar(range(len(stats[year])), [i[1]
                                                           for i in stats[year]], align='center')
        plots[index].set_xticks(range(len(stats[year])))
        plots[index].set_xticklabels([i[0] for i in stats[year]])
        plots[index].set_title(f"Year{year}", )
        plots[index].set(xlabel='Regions', ylabel='Count of crashes')
        for s in ['top', 'right']:
            plots[index].spines[s].set_visible(False)
        for rect in rects:
            height = rect.get_height()
            plots[index].annotate(str(height), (rect.get_x(
            ) + rect.get_width()/2, height + 500.0),  ha='center', va='bottom')

    plt.ylim(0, max(values) + 3000)
    fig.tight_layout()

    if fig_location:
        if not path.exists(fig_location):
            mkdir(fig_location)
        plt.savefig(
            f"{fig_location}/statistic_{'_'.join([i[0] for i in stats['2016']])}.png")

    if show_figure:
        plt.show()


if __name__ == "__main__":
    parser = ArgumentParser(
        description='Plot statistics of car crashes in Czech Republic')
    parser.add_argument('--show_figure', type=bool, default=False)
    parser.add_argument('--fig_location', type=str, default=None)
    args = parser.parse_args()
    regions = [""]
    while not all([len(a) == 3 for a in regions]):
        regions = input(
            "Choose regions for statistics (REG REG ...) or leave empty for all regions: ").split(" ")
        if regions == [""]:
            regions = None
            break
        print("Please provide regions code such as PHA fro Praha a t.d")

    result = DataDownloader().get_list(regions)
    plot_stat(result, fig_location=args.fig_location,
              show_figure=args.show_figure)
