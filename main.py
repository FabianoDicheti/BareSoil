# -*- coding: utf-8 -*-
"""

@author: fabiano dicheti
"""
# sudo docker build -t bare .
#sudo docker run --rm -v $(pwd)/static:/app/static bare
import os
from BareSoilEstimation import BareSoil
from CommonEstimation import CommonBare
from utils import read_tif_images, download_from_kml
from plots import plot_decomposition
from ndvirgb import convert_ndvi_image

def main():

    destination = './static'
    if not os.path.exists(destination):
        os.makedirs(destination)
    
    verify_kml_files = os.listdir("./kmlFiles")
    
    error_book = []
    offset_list = []

    # download infrared images
    if len(verify_kml_files) > 0:
        offset_list, images_list, error = download_from_kml('2023-05-05', ['B2','B4','B8'])
        error_book.append(error)
        image_directory = './static'
        if len(images_list) == 0:
            image_directory = './imageSamples'
            error_book.append('not a single image was downloaded from kml files, check errors above.')

    else:
        image_directory = './imageSamples'
        error_book.append('no kml found in dir: kmlFiles, using images from dir: ./imageSamples')
        
    images, names = read_tif_images(image_directory)
    
    proposed = []
    simplified_percent = []
    winter_decomposition = []

    # apply both methods to estimate bare soil
    for red_band, nir_band in images:

        algorithm, decomposition_endmembers = BareSoil.threshold_percentage(red_band, nir_band)
        proposed.append(algorithm)
        winter_decomposition.append(decomposition_endmembers)
        simplified_percent.append(CommonBare.common_bare_percent(red_band, nir_band))
        
    try:
        for item in os.listdir('./static'):
            arquivo = os.path.join('./static', item)
            convert_ndvi_image(arquivo)
    except Exception as e:
        error_book.append(e)
        
    # download RGB images to analisis
    if len(verify_kml_files) > 0:
         offset_list, images_list, error = download_from_kml('2023-05-05', ['B4','B3','B2'])
         error_book.append(error)
         image_directory = './static'
         if len(images_list) == 0:
             image_directory = './imageSamples'
             error_book.append('not a single image was downloaded from kml files, check errors above.')
    else:
         print('no kml for imagens to RGB download')
    
    # plot decomposition graph
    try:
        for i in range(len(proposed)):
            plot_decomposition(winter_decomposition[i], names[i])
    except Exception as e:
        error_book.append(e)
        
    # print block
    print('diretorio imagens -->', os.listdir('./static'))
    print(30*'_','\n\n   RESULTS \n')
    
    for i in range(len(proposed)):
        print(f"File Name -> {names[i]}")
        if len(offset_list) > i:
            print(f" offset -> {offset_list[i]}")
        print("Proposed Algorithm: /  Simplified Method Percent ")
        print(f"     {proposed[i]}        /     {simplified_percent[i]} \n")
        print(f"decomposition {winter_decomposition[i]}")
        
    print('check |     errors -----> ', error_book)
    print("-- > look for results on ./static folder!")
    

if __name__ == "__main__":
    main()

