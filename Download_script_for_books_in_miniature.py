"""
Marion Charpier
---
This script was produced as part of an M2 TNAH internship at the École des Chartes,
under the joint supervision of the University of Humboldt (Berlin) and the IRHT-CNRS (Paris).
---
"""
# Download script for miniatures in folio and for books in miniatures

import re
import pandas as pd
import os
import requests, time
import shutil
from PIL import Image

def download_image_from_url(image_url, dir_path, request_pause):
    """
    Downloads an image from an url and stores it as a file.
    """
    
    print(f'Downloading image from {image_url}')

    try:
        r = requests.get(image_url, stream=True)
        print(r.status_code)
        # Check if image was retrieved successfully
        if r.status_code == 200:
            r.raw.decode_content = True

            with open(dir_path, 'wb') as image_file:
                shutil.copyfileobj(r.raw, image_file)
            # recommended request_pause = 10 seconds
            time.sleep(request_pause)
        else:
            print(f"Failed to download image from {image_url}. Status code: {r.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"SSL Error occurred while downloading image from {image_url}. Error message: {str(e)}")
    except Exception as e:
        print(f"Error occurred while downloading image from {image_url}. Error message: {str(e)}")

def from_absolute_relative(absolute_coordinates, img_height, img_width):

    if absolute_coordinates:
        x_abs, y_abs, height_abs, width_abs = map(int, absolute_coordinates.split(","))
        x_rel = x_abs / img_width
        y_rel = y_abs / img_height
        width_rel = width_abs / img_width
        height_rel = height_abs / img_height
        return f'{x_rel}, {y_rel}, {width_rel}, {height_rel}'
        # print(f"relative x: {x_rel}, relative y: {y_rel}, relative width: {width_rel}, relative height: {height_rel}")


# Read in the CSV files
horae_csv = pd.read_csv('Export_horae_t98.csv')
books_csv = pd.read_csv('Books_in_Books.csv', sep=';')

# Get a list of all the image URLs in books_csv
books_urls = list(books_csv['Image_url'])

# Iterate over each row in horae_csv
for _, row in horae_csv.iterrows():
    # Get the image URL, the institution and the shelfmark, the iiif manifest and the image canvas' number in the manifest from the current row
    horae_url = row['image_URL']
    horae_ms_name = row['rec_Title_full']
    horae_manifest = row['iiif manifest']
    horae_iiif_nb = row['image # in iiif manifest']

    # The basis of the image name is horae_ms_name, with spaces replaced by "_".
    basename = re.sub(r"[^\w]+", "_", horae_ms_name)
    # print(filename)
    
    # Extract the boundind box coordinates
    box_coordinates = re.search(r"\d+,\d+,\d+,\d+", horae_url).group()
    # print(box_coordinates)

    # Get the URL of the full image
    full_image_url = re.sub(r"\d+,\d+,\d+,\d+", "full", horae_url)
    # print(full_image_url)

    # Check if the image URL is in books_urls
    if horae_url in books_urls:
        # If the URL is in books_urls, add the iiif manifest to the 'Manifest_URL' column in books_csv
        books_csv.loc[books_csv['Image_url'] == horae_url, 'Full_image_url'] = full_image_url
        books_csv.loc[books_csv['Image_url'] == horae_url, 'Manifest_URL'] = horae_manifest
        books_csv.loc[books_csv['Image_url'] == horae_url, 'Image_basename'] = basename
        books_csv.loc[books_csv['Image_url'] == horae_url, 'Image_#_in_manifest'] = horae_iiif_nb
        books_csv.loc[books_csv['Image_url'] == horae_url, 'Folio_filename'] = f"{basename}_{horae_iiif_nb}"
        books_csv.loc[books_csv['Image_url'] == horae_url, 'Miniature_coordinates'] = box_coordinates
        books_csv.loc[books_csv['Image_url'] == horae_url, 'Miniature_filename'] = f"{basename}_{horae_iiif_nb}_{box_coordinates}"


# Save the updated books_csv
books_csv.to_csv('Books_in_Books.csv', sep=';', index=False)

# Create the directory where to save images
output_folder = 'training_1'

#This folder is for the miniatures where the books will be annotated
miniatures_folder = 'data/Miniatures' 
miniatures_folder = os.path.join(miniatures_folder, output_folder)

if not os.path.exists(miniatures_folder):
    os.makedirs(miniatures_folder)
    print(f'Miniatures downloaded in {miniatures_folder}')

#This folder is for the entire folio for miniatures detection
folio_folder = 'data/Folios' 
folio_folder = os.path.join(folio_folder, output_folder)

if not os.path.exists(folio_folder):
    os.makedirs(folio_folder)
    print(f'Folios downloaded in {folio_folder}')

# Iterate over each row in books_csv
for _, row in books_csv.iterrows():
    # Get the image URL, the miniature coordinates and the filename from the current row
    image_url = row['Image_url']
    folio_url = row['Full_image_url']
    miniature_coordinates = row['Miniature_coordinates']
    miniature_filename = row['Miniature_filename']
    folio_filename = row['Folio_filename']
    
    # Check if the miniature_filename is not empty
    if miniature_filename:
        output_file_path = os.path.join(miniatures_folder, miniature_filename + '.jpg')
        if os.path.exists(output_file_path):
            print(f"The image {output_file_path} already dowloaded")
            books_csv.loc[books_csv['Image_url'] == image_url, 'Miniature_filepath'] = output_file_path
        else:
        # Download the image
            download_image_from_url(image_url, output_file_path, 10)
        try:
            books_csv.loc[books_csv['Image_url'] == image_url, 'Miniature_filepath'] = output_file_path
        except:
            output_file_path = ''

    if folio_url:
        output_file_path = os.path.join(folio_folder, folio_filename + '.jpg')
        if os.path.exists(output_file_path):
            print(f"The image {output_file_path} already dowloaded")
        else:
            download_image_from_url(folio_url, output_file_path, 10)
        
        try:
            books_csv.loc[books_csv['Image_url'] == image_url, 'Folio_filepath'] = output_file_path

            img_height, img_width = Image.open(output_file_path).size
            relative_coords = from_absolute_relative(box_coordinates, img_height, img_width)
            books_csv.loc[books_csv['Image_url'] == image_url, 'FolioHeightAsDownloaded'] = img_height
            books_csv.loc[books_csv['Image_url'] == image_url, 'FolioWidthAsDownloaded'] = img_width
            books_csv.loc[books_csv['Image_url'] == image_url, 'relative_coordinates'] = relative_coords
        except:
            output_file_path = ''
            img_height =''
            img_width = ''
            relative_coords = ''

    books_csv.to_csv('Books_in_Books.csv', sep=';', index=False)