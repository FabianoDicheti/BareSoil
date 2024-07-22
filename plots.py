#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: fabiano 
"""

import matplotlib.pyplot as plt
import os

def plot_decomposition(decomposition, file_name):
    """
    Plots the decomposition data on a Cartesian plane.

    Parameters:
    decomposition (list of lists): The decomposition data to plot.
    file_name (str): The name of the file associated with the decomposition data.
    """
    # Flatten the decomposition data
    x_values = [pair[0] for pair in decomposition]
    y_values = [pair[1] for pair in decomposition]
    mean_values = [(x+y)/2 for x, y in zip(x_values, y_values)]
    
    # Determine the indices for the special points
    max_x_index = x_values.index(max(x_values))
    min_mean = mean_values.index(min(mean_values))
    

    # Define the colors for the points
    point_colors = ['red'] * len(x_values)
    point_colors[min_mean] = 'black'
    point_colors[max_x_index] = 'blue'

    # Plotting
    plt.figure()
    
    # Plot each point with its respective color
    for i in range(len(x_values)):
        plt.scatter(x_values[i], y_values[i], color=point_colors[i], marker='o')
    
    # Connect all points with black lines
    plt.plot(x_values, y_values, linestyle='-', color='black')

    # Adding title and labels
    plt.title(f'Decomp {file_name}')
    plt.xlabel('NIR BAND')
    plt.ylabel('RED BAND')

    # Ensure the static directory exists
    output_dir = '/app/static'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the plot
    plt.savefig(os.path.join(output_dir, f'{file_name}_decomp.png'))
    plt.close()
