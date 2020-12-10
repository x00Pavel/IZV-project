#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np


def make_geo(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym
    kodovani."""
    df = df[df['region'].isin(['JHM'])][["region", "d", "e", "p5a"]]
    gdf = gpd.geodataframe.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.d, df.e), crs="EPSG:5514")
    gdf.to_crs(epsg=3857, inplace=True)
    return gdf


def plot_geo(gdf: gpd.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s dvemi podgrafy podle lokality nehody """

    fig, (ax1, ax2) = plt.subplots(1, 2)

    gdf[gdf["p5a"] == 1].plot(ax=ax1, color="darkred", markersize=2)
    gdf[gdf["p5a"] == 2].plot(ax=ax2, color="green", markersize=2)

    ax1.axis('off')
    ax2.axis('off')

    ax1.set_title("Crashes in JHM in cityes")
    ax2.set_title("Crashes in JHM in outside cityes")

    ax2.set_ylim((ax1.get_ylim()))
    ax2.set_xlim((ax1.get_xlim()))

    ctx.add_basemap(ax1, crs=gdf.crs.to_string(),
                    source=ctx.providers.Stamen.TonerLite)

    ctx.add_basemap(ax2, crs=gdf.crs.to_string(),
                    source=ctx.providers.Stamen.TonerLite)

    if fig_location:
        plt.savefig(fig_location)
    if show_figure:
        plt.show()
    plt.close()


def plot_cluster(gdf: gpd.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do
    clusteru."""


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
