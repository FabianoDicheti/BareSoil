# -*- coding: utf-8 -*-
"""

@author: fabiano dicheti
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal
from BareSoilEstimation import BareSoil
from CommonEstimation import CommonBare


def read_tif_images(directory):
    f_names = []
    images = []
    for file_name in os.listdir(directory):

        if file_name.endswith('.tif'):
            f_names.append(file_name)
            file_path = os.path.join(directory, file_name)
            dataset = gdal.Open(file_path)
            red_band = dataset.GetRasterBand(1).ReadAsArray()
            nir_band = dataset.GetRasterBand(2).ReadAsArray()
            images.append((red_band, nir_band))
    return images, f_names



def main():
    image_directory = './ImageSamples'
    images, names = read_tif_images(image_directory)
    
    proposed = []
    simplified_percent = []

    for red_band, nir_band in images:

        proposed.append(BareSoil.threshold_percentage(red_band, nir_band))
        
        simplified_percent.append(CommonBare.common_bare_percent(red_band, nir_band))
        
    for i in range(len(proposed)):
        
        print(f"File Name -> {names[i]}")
        print("Proposed Algorithm: /  Simplified Method Percent ")
        print(f"     {proposed[i]}        /     {simplified_percent[i]} \n")


if __name__ == "__main__":
    main()
