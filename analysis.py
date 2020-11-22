#!/usr/bin/python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz
from sys import getsizeof
from pickle import load
import gzip as gz


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    df = None
    with gz.open(filename, 'rb') as f:
        df = load(f)
    if verbose:
        print(f"orig_size={getsizeof(df)/1_048_576:.2f} MB")

    for col in df.columns:
        df[col].replace(r'(^\s*$)|-1', np.NAN, inplace=True, regex=True)
        if col in ["p36", "p37", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9",  
                   "p10", "p11", "p12", "p13a", "p13b", "p13c", "p14", "p15",
                   "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24",
                   "p27", "p28", "p34", "p35", "p39", "p44", "p45a", "p47", 
                   "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a", 
                   "p57", "p58", "a", "b", "d", "e", "f", "g", "j", "p5a",
                   ]:
            df[col] = pd.to_numeric(
                df[col], downcast='signed')
        elif col == "p2a":
            df["p2a"] = pd.to_datetime(df["p2a"])
            df["date"] = df["p2a"].copy()
        if col in ["p1", "k", "l", "n", "o", "p", "q", "r", "s", "t", "h", "i", "region"]:
            df[col] = df[col].astype("category")

    if verbose:
        print(f"new_size={getsizeof(df)/1_048_576:.2f} MB")

    return df


def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    res = df[["region", "p13a", "p13b", "p13c", "p1"]]
    resm = pd.melt(res, id_vars=["region"], value_vars=("p13a", "p13b", "p13c"), var_name="variable",
                   value_name="count").groupby(["region", "variable"]).agg("sum").reset_index()
    rest = res[["region", "p1"]].groupby(["region"]).agg("count").reset_index().melt(
        var_name="variable", value_vars=("p1"), value_name="count", id_vars="region")
    res = pd.concat([resm, rest])
    order = res.loc[res["variable"] == "p1"].sort_values(
        ["count"], ascending=False)['region']
    fg = sns.FacetGrid(res,
                       row="variable",
                       sharex=True,
                       sharey=False,
                       height=3.5,
                       aspect=3)
    # set plots on grid
    fg.map(sns.barplot, 'region', 'count', order=order, palette="deep")
    axes = fg.axes.flatten()
    axes[0].set_title("Deaths")
    axes[1].set_title("Hard harm")
    axes[2].set_title("Light harm")
    axes[3].set_title("Count of crashes")
    for ax in axes:
        for p in ax.patches:
            ax.annotate(round(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 10), textcoords='offset points')
    
    if fig_location is not None:
        plt.savefig(fig_location)
    if show_figure:
        plt.show()



# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    pass

# Ukol 4: povrch vozovky


def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass


if __name__ == "__main__":
    pass
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz", True)
    plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    plot_damage(df, "02_priciny.png", True)
    # plot_surface(df, "03_stav.png", True)
