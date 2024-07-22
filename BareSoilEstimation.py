# -*- coding: utf-8 -*-
"""

@author: fabiano dicheti
"""
import numpy as np

class BareSoil:
    @staticmethod
    def shadow_point(R_band, NIR_band):
        '''
        Calculates the shadow point of a two-channel decomposition
        one Red and one Infrared

        Parameters
        ----------
            R_band: (array)
                Numpy array containing the red channel of the image
            NIR_band: (array)
                Numpy array containing the infrared channel of the image

        Returns
        -------
            [S0, S1]: (list)
                Coordinates of the shadow point of the image (row x column)
            S_ndvi: (float)
                NDVI value of the shadow point
        '''

        combination = np.add(R_band, NIR_band)
        shadow = np.min(combination[np.nonzero(combination)])
        S_index = np.where(combination == shadow)

        S0 = round(S_index[0][0], 5)
        S1 = round(S_index[1][0], 5)

        nir = NIR_band[S0][S1]
        red = R_band[S0][S1]
        if nir == red:
            nir = nir + 0.001

        S_ndvi = (nir - red) / (nir + red)

        return [S0, S1], S_ndvi

    @staticmethod
    def endmembers(R_band, NIR_band):
        '''
        Finds the points of the branches of the red channel (Endmember A) and
        infrared channel (Endmember B), for each Endmember, the NDVI value is calculated.

        Parameters
        ----------
        R_band : (array)
            Numpy array containing the red channel of the image
        NIR_band : (array)
            Numpy array containing the infrared channel of the image

        Returns
        -------
        [R0, R1]: (list)
            Row and column of the highest value red pixel
        [N0, N1]: (list)
            Row and column of the highest value infrared pixel
        NDVI_Rmax : (float)
            NDVI as a function of the highest red pixel.
        NDVI_Nmax : (float)
            NDVI as a function of the highest infrared pixel.
        '''

        # define the highest value of the red matrix
        R_max = np.max(R_band)
        # define the highest value of the infrared matrix
        N_max = np.max(NIR_band)

        # find the indices of the highest value of the red matrix
        R_index = np.where(R_band == R_max)

        # find the indices of the highest value of the infrared matrix
        N_index = np.where(NIR_band == N_max)

        # ENDMEMBER A
        R0 = R_index[0][0]
        R1 = R_index[1][0]

        # ENDMEMBER B
        if len(N_index[0]) > 1:
            if N_index[0][0] == R_index[0][0]:
                N0 = N_index[0][1]
                N1 = N_index[1][1]
            else:
                N0 = N_index[0][0]
                N1 = N_index[1][0]
        else:
            N0 = N_index[0][0]
            N1 = N_index[1][0]

        # calculate the NDVI of ENDMEMBER A (red)
        red_a = R_band[R0][R1]
        nir_a = NIR_band[R0][R1]

        if red_a == nir_a:
            nir_a = nir_a + 0.01

        NDVI_Rmax = (nir_a - red_a) / (nir_a + red_a)

        # calculate the NDVI of ENDMEMBER B (infrared)
        red_b = R_band[N0][N1]
        nir_b = NIR_band[N0][N1]

        if red_b == nir_b:
            nir_b = nir_b + 0.01

        NDVI_Nmax = (nir_b - red_b) / (nir_b + red_b)
        
        return [R0, R1], [N0, N1], NDVI_Rmax, NDVI_Nmax

    @staticmethod
    def ndvi_threshold(red_channel, infra_channel, n_lambda=0.4):
        '''
        Parameters
        ----------
        image : (str)
            String containing the path to the image to be analyzed
        n_lambda : (float), optional
            Value of the channel decomposition constant, the default is 0.4.

        Returns
        -------
        Float
            NDVI threshold value, below which it is considered that the pixel
            represents exposed soil.
        '''


        shadow_point, shadow_ndvi = BareSoil.shadow_point(red_channel, infra_channel)
        endmember_red, endmmember_nir, red_ndvi, infra_ndvi = BareSoil.endmembers(red_channel, infra_channel)

        endmembers_decomposition = [shadow_point, endmember_red, endmmember_nir]

        return np.min([(red_ndvi * n_lambda), (infra_ndvi * n_lambda), shadow_ndvi]), endmembers_decomposition

    @staticmethod
    def threshold_percentage(red_channel, infra_channel):
        '''
        Method to calculate what percentage of the image is below the exposed soil threshold

        Parameters
        ----------
        image : (str)
            String containing the path to the image to be analyzed

        Returns
        -------
        (Float)
            Percentage of exposed soil in the image
        '''


        red_list = []
        infra_list = []

        for i in range(len(red_channel)):
            for j in range(len(red_channel[0])):
                red_list.append(red_channel[i][j])
                infra_list.append(infra_channel[i][j])

        ndvi_list = []
        zero_count = 0
        for n in range(len(red_list)):
            if red_list[n] != 0:
                R = round(red_list[n], 5)
                N = round(infra_list[n], 5)
                if N > 0.001:
                    N = N + 0.001
                ndvi = (N - R) / (N + R)
                ndvi_list.append(ndvi)
            else:
                zero_count += 1

        threshold, endmembers_decomposition = BareSoil.ndvi_threshold(red_channel, infra_channel)

        count = len([i for i in ndvi_list if i <= threshold])

        percentage = count / len(ndvi_list)
        percent_f = "{:.5f}".format(percentage)

        return percent_f, endmembers_decomposition
