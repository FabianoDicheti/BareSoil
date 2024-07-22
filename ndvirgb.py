#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: fabiano 
"""

from osgeo import gdal #do not remove this line
from PIL import Image
import os
import numpy as np
import imageio


def img_scale(tif_path, target_path):
    """
    Scales an image and converts it to Byte format using GDAL.

    Args:
    -----------
        tif_path: str
            The path to the input TIFF file.
        target_path: str
            The path to save the scaled output TIFF file.

    Returns:
    -----------
        None
    """
    
    os.system("gdal_translate -of GTiff -ot Byte -scale 0.0 0.99 0 255 " +
              tif_path +
              " " +
              target_path)


def ndvi_pixel(red, nir):
    """
    Calculates the NDVI (Normalized Difference Vegetation Index) for a given pixel.

    Args:
    -----------
        red: float
            The reflectance value of the red band.
        nir: float
            The reflectance value of the near-infrared band.

    Returns:
    -----------
        ndvi: float
            The NDVI value for the given pixel. Returns 0.0 in case of division by zero or any other exception.
    """
    try:
        ndvi = (nir - red) / (nir + red)
    except ZeroDivisionError:
        # If there is a division by zero, set NDVI to zero
        ndvi = 0.0
    except Exception as e:
        # Handle other types of exceptions, if necessary
        print(f"Error calculating NDVI: {e}")
        ndvi = 0.0
    return ndvi


def ndvi_to_rgb(ndvi_matrix, ref):
    """
    Converts an NDVI matrix to an RGB image based on predefined color mappings.

    Args:
    -----------
        ndvi_matrix: np.ndarray
            A matrix containing NDVI values.
        ref: str
            A reference string used for naming the output image file.

    Returns:
    -----------
        image_name: str
            The path to the saved RGB image.
    """
    # Mapping of NDVI value ranges to RGB colors
    ndvi_colors = [
        (0.0000, (66, 46, 36)),
        (0.0208, (72, 50, 40)),
        (0.0417, (79, 55, 44)),
        (0.0625, (85, 59, 47)),
        (0.0833, (92, 64, 51)),
        (0.1042, (98, 68, 55)),
        (0.1250, (105, 73, 58)),
        (0.1458, (112, 78, 62)),
        (0.1667, (118, 82, 65)),
        (0.1875, (125, 87, 69)),
        (0.2083, (131, 91, 73)),
        (0.2292, (138, 96, 76)),
        (0.2500, (253, 229, 165)),
        (0.2708, (253, 226, 155)),
        (0.2917, (253, 223, 145)),
        (0.3125, (253, 220, 135)),
        (0.3333, (253, 217, 125)),
        (0.3542, (253, 214, 115)),
        (0.3750, (252, 211, 105)),
        (0.3958, (252, 208, 95)),
        (0.4167, (252, 205, 84)),
        (0.4375, (252, 202, 74)),
        (0.4583, (252, 199, 64)),
        (0.4792, (252, 197, 56)),
        (0.5000, (205, 234, 143)),
        (0.5208, (201, 232, 135)),
        (0.5417, (197, 231, 126)),
        (0.5625, (194, 229, 118)),
        (0.5833, (190, 228, 109)),
        (0.6042, (186, 226, 100)),
        (0.6250, (182, 224, 92)),
        (0.6458, (178, 223, 83)),
        (0.6667, (174, 221, 75)),
        (0.6875, (171, 220, 66)),
        (0.7083, (167, 218, 57)),
        (0.7292, (163, 216, 49)),
        (0.7500, (35, 200, 87)),
        (0.7708, (33, 191, 83)),
        (0.7917, (32, 183, 79)),
        (0.8125, (30, 174, 75)),
        (0.8333, (29, 165, 72)),
        (0.8542, (27, 156, 68)),
        (0.8750, (26, 148, 64)),
        (0.8958, (24, 139, 60)),
        (0.9167, (23, 130, 57)),
        (0.9375, (21, 122, 53)),
        (0.9583, (20, 113, 49)),
        (0.9792, (18, 104, 45)),
        (1.0000, (17, 96, 41))
    ]

    # Create an empty matrix for the RGB image
    rgb_image = np.zeros((ndvi_matrix.shape[0], ndvi_matrix.shape[1], 3), dtype=np.uint8)

    # Assign the corresponding color to each pixel based on the NDVI value
    for i in range(len(ndvi_colors) - 1):
        lower_bound, lower_color = ndvi_colors[i]
        upper_bound, _ = ndvi_colors[i + 1]

        mask = (ndvi_matrix >= lower_bound) & (ndvi_matrix < upper_bound)
        rgb_image[mask] = lower_color

    # Handle the case where NDVI is exactly 1
    rgb_image[ndvi_matrix == 1] = ndvi_colors[-1][1]

    image_name = f"./static/{ref}_ndvi_rgb.png"
    
    imageio.imwrite(image_name, rgb_image)

    return image_name


def convert_ndvi_image(tif_image):
    """
    Converts a TIFF image to an NDVI image and saves it as a PNG file.

    Args:
    -----------
        tif_image: str
            The path to the input TIFF image.

    Returns:
    -----------
        ndvi_rgb_name: str
            The path to the saved NDVI RGB image.
    """
    
    png_image = tif_image.replace('.tif', '.png')

    os.system("gdal_translate -of GTiff -ot Byte -scale 0.0 0.99 0 255 " +
              tif_image +
              " " +
              png_image)
     
    eight_bits = png_image

    try:
        img_scale(tif_image, eight_bits)

        img = Image.open(eight_bits)
        matrix = np.array(img)
        red = matrix[:, :, 1]
        nir = matrix[:, :, 2]


        ndvi_matrix = []

        for i in range(len(red)):
            row = []
            for j in range(len(red[0])):
                ndvi = ndvi_pixel(red[i][j], nir[i][j])
                row.append(ndvi)
            ndvi_matrix.append(row)

        ndvi_matrix = np.array(ndvi_matrix)

        r = png_image.replace('.png', '__')
        R = r.replace('./static/', '')
        ref = R
        ndvi_rgb_name = ndvi_to_rgb(ndvi_matrix, ref)

    except Exception as e:
        print(f"Error converting NDVI image: {e}")

    return ndvi_rgb_name



