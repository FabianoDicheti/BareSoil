# -*- coding: utf-8 -*-
"""

@author: fabiano dicheti
"""
import numpy as np

class CommonBare:
    @staticmethod
    def calculate_ndvi(red_band, nir_band):
        """
        Calculates the NDVI from red and NIR bands.

        Parameters
        ----------
        red_band : array
            Numpy array containing the red channel of the image.
        nir_band : array
            Numpy array containing the NIR channel of the image.

        Returns
        -------
        array
            Numpy array containing the NDVI values.
        """
        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = (nir_band - red_band) / (nir_band + red_band)
            ndvi[np.isinf(ndvi)] = 0
            ndvi[np.isnan(ndvi)] = 0
        return ndvi

    @staticmethod
    def common_bare_percent(red_band, nir_band):
        """
        Calculates the percentage of common bare soil within an NDVI array.

        Parameters
        ----------
        red_band : array
            Numpy array containing the red channel of the image.
        nir_band : array
            Numpy array containing the NIR channel of the image.

        Returns
        -------
        float
            Percentage of common bare soil in the NDVI array.
        """
        ndvi_array = CommonBare.calculate_ndvi(red_band, nir_band)

        if ndvi_array.size == 0:
            return 0

        count = np.sum((ndvi_array >= -0.1) & (ndvi_array <= 0.1))
        total = ndvi_array.size
        percentage = count / total

        return round(percentage, 5)
