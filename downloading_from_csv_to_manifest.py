"""
Marion Charpier
---
This script was produced as part of an M2 TNAH internship at the École des Chartes,
under the joint supervision of the University of Humboldt (Berlin) and the IRHT-CNRS (Paris).
---

The following script is used to download images of digitised manuscripts with an IIIF manifest from a .csv file containing the image data used to train a model (YOLOv8) for book detection in the miniatures of Books of Hours.
Each manifest is saved in a folder named after the manuscript, and each image in the manifest is then uploaded to the same folder. At the end of the download, a csv file is created with the data for each of the images in the manifest, whether or not they have been downloaded. This data will be used to create manifests enriched with bounding box annotations after detection using the trained model.

Translated with www.DeepL.com/Translator (free version)

"""

import os
import pandas as pd
import requests
import shutil
import time
import json
import cv2
from PIL import Image


def download_image_from_url(image_url, dir_path, request_pause):
    """
    Downloads an image from an url and stores it as a file.
    """

    print(f'Downloading image from {image_url}')

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
        print(f"Fehler {r.status_code}")

def open_json_file(json_file_name):
    """Opens a JSON file and returns it as a dictionary."""

    with open(json_file_name, 'r') as json_file:
        return json.load(json_file)

def download_images_from_manifest(manifest_URL, folder, ms_base_name, request_pause):
    """
    Downloads all images from a IIIF manifest. All images are named with the name of the IIIF manifest (file) and
    after an underscore, the label of the images' canvas.
    """
    print(f'Downloading all images from {manifest_URL}')
    waittime = request_pause
    
    response = requests.get(manifest_URL)    
    print(response.status_code)
    if response.status_code == 200:
        iiif_manifest = response.json()
    else:
        iiif_manifest = None
    
    # Create a list to store image information
    images_data = []

    # Download images
    for i, canvas in enumerate(iiif_manifest['sequences'][0]['canvases']):
        manifestURL = iiif_manifest['@id']
        canvasId = canvas['@id']
        urlImage = canvas['images'][0]['resource']['@id']
        imageLabel = canvas['label']
        imageWidthAsDeclared = canvas['width']
        imageHeightAsDeclared = canvas['height']
        image_format = urlImage.split('.')[-1]
        image_id = f"{i+1}"
        htmlCode = requests.get(urlImage)
        path_to_store_image = os.path.join(folder, ms_base_name + '_' + image_id + '.' + "jpg")
       
       # Check if the images are downloaded and don't downloaded again
        if os.path.exists(path_to_store_image):
            print(f"Image {path_to_store_image} already dowloaded ")
            htmlCode = 200
            imageFileName = os.path.join(folder, ms_base_name + '_' + image_id + '.' + "jpg")
            with Image.open(imageFileName) as img:
                imageWidthAsDownloaded, imageHeightAsDownloaded = img.size
        # If they are not dowloaded download them and add the post_download data
        else:
            download_image_from_url(urlImage, path_to_store_image, waittime)
        
            try:
                htmlCode = requests.get(urlImage).status_code
                imageFileName = os.path.join(folder, ms_base_name + '_' + image_id + '.' + "jpg")
                with Image.open(imageFileName) as img:
                    imageWidthAsDownloaded, imageHeightAsDownloaded = img.size

            except:
                htmlCode = ""
                imageFileName = ""
                imageWidthAsDownloaded = ""
                imageHeightAsDownloaded = ""

        # Add image data to the list
        image_data = {
            'manifestURL': manifestURL,
            'canvasId': canvasId,
            'urlImage': urlImage,
            'folderPath': os.path.join(folder, ms_base_name),
            'imageLabel': imageLabel,
            'imageWidthAsDeclared': imageWidthAsDeclared,
            'imageHeightAsDeclared': imageHeightAsDeclared,
            'htmlCode': htmlCode,
            'imageFileName': imageFileName,
            'imageWidthAsDownloaded': imageWidthAsDownloaded,
            'imageHeightAsDownloaded': imageHeightAsDownloaded
        }
        images_data.append(image_data)
    
    # Create a DataFrame from the image data list
    df = pd.DataFrame(images_data)
    
    # Save DataFrame to a CSV file
    csv_filename = os.path.join(folder, 'image_data.csv')
    df.to_csv(csv_filename, index=False)
    
    print(f"Image data saved to {csv_filename}")
    print('Downloads complete')

def download_data(csv_data, folder):
    df = pd.read_csv(csv_data, sep=';')

    # Parcourir chaque ligne du fichier CSV
    for i, row in df.iterrows():
        url_manifest = row['Manifest_URL']
        ms_name = row['Image_basename']

        outputfolder = os.path.join(folder, ms_name)
        
        # Vérifier si le dossier de destination existe, sinon le créer
        if not os.path.exists(outputfolder):
            os.makedirs(outputfolder)
        
        # Télécharger le fichier manifest.json
        response = requests.get(url_manifest)
        if response.status_code == 200:
            # Construire le chemin complet du fichier de destination
            chemin_destination = os.path.join(outputfolder, ms_name + '_manifest.json')
            
            # Enregistrer le fichier manifest.json dans le dossier de destination
            with open(chemin_destination, 'wb') as f:
                f.write(response.content)
                
            print(f'Le fichier manifest.json a été téléchargé et enregistré dans {outputfolder}')
            print()
            print(f'Téléchargement des images depuis {url_manifest}')

            # Télécharger les images du manifeste
            download_images_from_manifest(url_manifest, outputfolder, ms_name, 5)
        else:
            print(f'Échec du téléchargement du fichier manifest.json pour {ms_name}')


download_data('filepath.cvs', 'folder')
