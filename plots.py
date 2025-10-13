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
    x_values = [pair[0] for pair in decomposition]
    y_values = [pair[1] for pair in decomposition]
    mean_values = [(x+y)/2 for x, y in zip(x_values, y_values)]
    
    max_x_index = x_values.index(max(x_values))
    min_mean = mean_values.index(min(mean_values))
    
    point_colors = ['red'] * len(x_values)
    point_colors[min_mean] = 'black'
    point_colors[max_x_index] = 'blue'

    plt.figure()
    
    for i in range(len(x_values)):
        plt.scatter(x_values[i], y_values[i], color=point_colors[i], marker='o')
    
    # Connect all points with black lines
    plt.plot(x_values, y_values, linestyle='-', color='black')

    plt.title(f'Decomp {file_name}')
    plt.xlabel('NIR BAND')
    plt.ylabel('RED BAND')

    output_dir = '/app/static'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.savefig(os.path.join(output_dir, f'{file_name}_decomp.png'))
    plt.close()
