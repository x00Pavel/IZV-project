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
    df = df[df['region'].isin(['JHM'])][["p1", "d", "e", "p5a"]].replace(
        [np.inf, -np.inf], np.nan).dropna()
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
    gdf_c = gdf.to_crs("EPSG:5514")  # spravny system pro praci s velikostmi
    gdf_c = gdf_c.set_geometry(gdf_c.centroid).to_crs(epsg=3857)
    coords = np.dstack([gdf_c.geometry.x, gdf_c.geometry.y]).reshape(-1, 2)
    db = sklearn.cluster.MiniBatchKMeans(n_clusters=15).fit(coords)

    gdf4 = gdf_c.copy()
    gdf4["cluster"] = db.labels_
    gdf4 = gdf4.dissolve(by="cluster", aggfunc={"p1": "count"})
    plt.figure(figsize=(20, 12))
    ax = plt.gca()
    ax.set_xlim((1728410.535110552, 1973672.565823917))
    ax.set_ylim((6220359.7750041215, 6387884.348316809))

    gdf_coords = gpd.GeoDataFrame(geometry=gpd.points_from_xy(
        db.cluster_centers_[:, 0], db.cluster_centers_[:, 1]))
    gdf5 = gdf4.merge(gdf_coords, left_on="cluster",
                      right_index=True).set_geometry("geometry_y")
    plt.axis("off")

    gdf.to_crs(epsg=3857).plot(
        ax=ax, color="tab:grey", alpha=0.5, markersize=5)
    gdf5.plot(ax=ax, markersize=gdf5["p1"],
              column="p1", legend=True, alpha=0.5)

    ctx.add_basemap(ax, crs="epsg:3857", source=ctx.providers.Stamen.TonerLite)
    if fig_location:
        plt.savefig(fig_location)
    if show_figure:
        plt.show()
    plt.close()


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
