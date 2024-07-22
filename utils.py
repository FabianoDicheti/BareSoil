#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: fabiano 
"""

import os
import ee
import geemap
from fastkml import kml
from fastkml import geometry
from geojson import Polygon
from osgeo import gdal
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta

def read_tif_images(directory):
    """
    Reads TIFF images from a specified directory and extracts the red and near-infrared (NIR) bands.

    This function scans the given directory for TIFF (.tif) files, reads each file, and extracts the 
    red and NIR bands from the raster data. It returns the extracted bands along with the file names.

    Parameters:
    directory (str): The path to the directory containing the TIFF files.

    Returns:
    tuple: A tuple containing:
        - images (list of tuples): A list where each element is a tuple containing two numpy arrays 
          representing the red and NIR bands of an image.
        - f_names (list of str): A list of file names of the TIFF images that were read.
    """
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


def simplify_kml(input_kml, output_kml):
    """
    Removes unnecessary markings and formatting details from a KML file.
    This is important to avoid contour errors when generating the GeoJSON.
    This method receives a KML file and returns the same file without the additional formatting.

    Parameters:
    input_kml (str): The path to the input KML file.
    output_kml (str): The path to the output simplified KML file.
    """
    
    with open(input_kml, 'r') as file:
        kml_content = file.read()

    tree = ET.fromstring(kml_content)
    coordinates = tree.findall('.//{http://www.opengis.net/kml/2.2}coordinates')[0].text

    coords_list = [tuple(map(float, coord.split(',')[:2])) for coord in coordinates.strip().split()]

    min_x = min(coord[0] for coord in coords_list)  # minimum longitude
    max_x = max(coord[0] for coord in coords_list)  # maximum longitude
    min_y = min(coord[1] for coord in coords_list)  # minimum latitude
    max_y = max(coord[1] for coord in coords_list)  # maximum latitude

    bbox = [min_x, min_y, max_x, max_y]
    
    tree = ET.parse(input_kml)
    root = tree.getroot()

    for elem in root.iter():
        elem.tag = elem.tag.split('}')[-1]

    kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    document = ET.SubElement(kml, 'Document')

    for placemark in root.iter('Placemark'):
        new_placemark = ET.Element('Placemark')
        for polygon in placemark.iter('Polygon'):
            new_placemark.append(polygon)
        document.append(new_placemark)

    tree = ET.ElementTree(kml)
    tree.write(output_kml, xml_declaration=True, encoding='utf-8')

    
    return bbox


def geo_json(kml_path):
    """
    Converts a KML file into a GeoJSON Polygon object.

    Parameters:
    -----------
    kml_path: str
        Path to the KML file that will be converted into GeoJSON.

    Returns:
    --------
    polygon: Polygon
        GeoJSON Polygon object containing the coordinates of the polygon defined in the KML.
    """

    kml_filename = kml_path
    with open(kml_filename, encoding="utf-8") as kml_file:
        doc = kml_file.read().encode('utf-8')
        k = kml.KML()
        k.from_string(doc)
        polygon_coords = []
        for feature0 in k.features():
            for feature1 in feature0.features():
                if isinstance(feature1.geometry, geometry.Polygon):
                    polygon = feature1.geometry
                    for coord in polygon.exterior.coords:
                        coord_tuple = (coord[0], coord[1])
                        # long, lat tuples
                        polygon_coords.append(coord_tuple)

    polygon = Polygon([polygon_coords])

    return polygon


def cloud_mask(image):
    """
    Applies a mask to clouds in a Google Earth Engine image.

    Args:
    -----------
        image: A Google Earth Engine image containing the 'QA60' band.

    Returns:
    -----------
        The image with clouds and cirrus masked.
    """
    qa60 = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa60.bitwiseAnd(cloud_bit_mask).eq(0)
    mask = qa60.bitwiseAnd(cirrus_bit_mask).eq(0)

    return image.updateMask(mask).divide(10000)


def download_from_gee(start_date, end_date, kml_name, bands):
    """
    Downloads images from Google Earth Engine and exports them in GeoTIFF format.

    Args:
    -----------
        start_date: str
            The start date for the image search.
        end_date: str
            The end date for the image search.
        kml_name: str
            The path to the KML file containing the polygon of interest.
        bands: list of str
            The list of bands to be selected from the image.

    Returns:
    -----------
        tuple:
            The path to the saved GeoTIFF file and the offset used for simplification.
    """
    
    destination_path = kml_name.replace('.kml', bands[2]+'.tif')
    destination_path = destination_path.replace('/kmlFiles/', '/static/')

    simplified_kml_name = kml_name.replace('.kml', '_simplified.kml')
    offset = simplify_kml(kml_name, simplified_kml_name)

    polygon = geo_json(simplified_kml_name)

    service_account = 'unioeste-fabiano@ee-fabiano-unioeste.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, './GEE_key/ee-fabiano-unioeste.json')
    ee.Initialize(credentials)

    image = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
             .filterDate(start_date, end_date)
             .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
             .map(cloud_mask)
             .filterBounds(polygon)
             .sort('CLOUD_COVER').first())

    img_bands = ee.Image(image).select(bands)

    geemap.ee_export_image(img_bands,
                           filename=destination_path,
                           scale=9,
                           crs='EPSG:4326',
                           region=polygon,
                           file_per_band=False)

    os.remove(simplified_kml_name)

    return destination_path, offset


def download_from_kml(date, bands):
    """
    Downloads images from Google Earth Engine for all KML files in the specified directory 
    and exports them in GeoTIFF format.

    Args:
    -----------
        date: str
            The reference date for the image search (format: 'YYYY-MM-DD').
        bands: list of str
            The list of bands to be selected from the images.

    Returns:
    -----------
        tuple:
            offset_list: list of float
                The list of offsets used for simplification for each KML file.
            images_list: list of str
                The list of paths to the saved GeoTIFF files.
            error_msg: list of str
                The list of error messages encountered during the process.
    """
    kmls = os.listdir("./kmlFiles")
    
    end_date = datetime.strptime(date, '%Y-%m-%d')
    start_date = end_date - timedelta(days=30)

    offset_list = []
    images_list = []
    error_msg = []
    
    for k_file in kmls:
        try:
            kml_file = os.path.join("./kmlFiles", k_file)
            img, offset = download_from_gee(start_date, end_date, kml_file, bands)
            
            images_list.append(img)
            offset_list.append(offset)
        except Exception as e:
            error_msg.append(f"For file ::: {k_file} ::: this error was found --> {e}")
    
    return offset_list, images_list, error_msg

