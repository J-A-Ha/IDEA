"""Functions for data visualisation."""

from typing import List, Dict, Tuple
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import igraph as ig
from igraph import Graph

def plot_timeline(dates: list, names: list, plot: str = 'created_at', units: str = 'months', intervals: int = 4, date_format: str = '%d.%m.%Y', colour: str = 'blue'):
        
        """
        Plots a timeline from a list of dates.
        
        Parameters
        ----------
        dates : list
            list of dates to plot.
        names : list
            list of labels for dates to plot.
        plot : str
            name of the time variable to plot from.
        units : str, default : 'months'
            units to use for plot.
        intervals : int
            intervals for plot (in units).
        date_format : str
            format for date.
        colour : str
            colour to use for plot.
        """
        
        # Choose levels
        levels = np.tile([-4, 4, -3, 3, -1, 1],
                         int(np.ceil(len(dates)/6)))[:len(dates)]

        # Create figure and plot a stem plot with the date
        fig, ax = plt.subplots(figsize=(8.8, 4), layout="constrained")
        ax.set(title=f"Item {plot} timeline")

        ax.vlines(dates, 0, levels, color="tab:" + colour)  # The vertical stems.
        ax.plot(dates, np.zeros_like(dates), "-o",
                color="k", markerfacecolor="w")  # Baseline and markers on it.

        # annotate lines
        for d, l, r in zip(dates, levels, names):
            ax.annotate(r, xy=(d, l),
                        xytext=(-3, np.sign(l)*3), textcoords="offset points",
                        horizontalalignment="right",
                        verticalalignment="bottom" if l > 0 else "top")

        # format x-axis with intervals based on user selection

        if units.lower() == 'days':
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=intervals))

        if units.lower() == 'months':
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=intervals))

        if units.lower() == 'years':
            ax.xaxis.set_major_locator(mdates.YearLocator())

        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

        # remove y-axis and spines
        ax.yaxis.set_visible(False)
        ax.spines[["left", "top", "right"]].set_visible(False)

        ax.margins(y=0.1)
        plt.show()

def plot_date_range_timeline(source, labels: str):
    
    """
    Plots a timeline from a source object containing a date range.
    
    Parameters
    ----------
    source : object
        data source to plot timeline.
    labels : str
        labels to plot.
    """
    
    # Declaring a figure "gnt"
    fig, gnt = plt.subplots(figsize=(8,6))

    # Need to fix hidden tick labels
    # https://stackoverflow.com/questions/43673659/matplotlib-not-showing-first-label-on-x-axis-for-the-bar-plot
    
    # Setting y-axis attributes
    y_tick_labels = labels
    y_pos = np.arange(len(y_tick_labels))

    gnt.set_yticks(y_pos)
    gnt.set_yticklabels(y_tick_labels)
    
    
    # Setting plot details
    for index, row in source.sort_values(by='start').reset_index().iterrows():
        
        # Retrieving and formatting date data
        item = row['Item']
        start_year = int(row.start.strftime("%Y"))
        duration = row['diff'].days/365
        
        # Updating plot
        gnt.broken_barh([(start_year, duration)], 
                        (index-0.5,0.8), 
                        facecolors =('tan')
                       )
        gnt.text(start_year+0.5, index-0.2, item)

def histogram(source):
    
    """
    Plots a histogram.
    """
    
    return plt.hist(source)

def plot_network(network: Graph, vertex_names: bool = True, edge_weights: bool = False, weight_by: str = 'weight'):
        
        """
        Plots a network diagram using matplotlib.
        
        Parameters
        ----------
        network : igraph.Graph
            network object to plot.
        vertex_names : bool
            whether to plot vertex names.
        edge_weights : bool
            whether to plot edge weights.
        weight_by : str
            name of edge attribute to use for edge weights.
        """
        
        # Copying network object to avoid side effects
        network_obj = copy.deepcopy(network)
        
        # Creating plot
        fig, ax = plt.subplots()
        
        # If 'edge_weights' labels are turned off and 'vertex_names' labels are turned off, 
        # plots figure without labels
        if (edge_weights == False) and (vertex_names == False):
            ig.plot(network_obj, 
                    target=ax
                   )
        
        # If 'edge_weights' labels are turned off and 'vertex_names' labels are on, 
        # plots figure without edge weight labels but with vertex 'name' attributes as vertex labels
        if (edge_weights == False) and (vertex_names == True):
            ig.plot(network_obj, 
                    target=ax,
                    vertex_label = network_obj.vs['name']
                   )
        # If 'edge_weights' labels are on and 'vertex_names' labels are turned off, 
        # plots figure a selected attribute 'weight_by' as edge labels
        # and without vertex labels
        if (edge_weights == True) and (vertex_names == False):
            ig.plot(network_obj, 
                    target=ax,
                    vertex_label = network_obj.vs['name']
                   )
        
        # If 'edge_weights' labels are on and 'vertex_names' labels are on, 
        # plots figure with vertex 'name' attributes as vertex labels
        # and a selected attribute 'weight_by' as edge labels
        if (edge_weights == True) and (vertex_names == True):
            ig.plot(network_obj, 
                    target=ax,
                    vertex_label = network_obj.vs['name'],
                    edge_label = network_obj.es[weight_by]
                   )