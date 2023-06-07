"""
Marion Charpier
---
This script was produced as part of an M2 TNAH internship at the École des Chartes,
under the joint supervision of the University of Humboldt (Berlin) and the IRHT-CNRS (Paris).
---
"""

import os
import shutil
import random

# This function cleans up the .txt file in the csv file to remove commas
def clean_comma(folder):
    for filename in os.listdir(folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder, filename)
            
            # Read the file content
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Remove commas
            content_without_comma = content.replace(',', '')
            
            # Write the modified content in the file
            with open(file_path, 'w') as file:
                file.write(content_without_comma)
                
# This function create three files one for each set : train, val and test
def create_txt_train_val_test(folder):
    # Get a list of the images
    files = os.listdir(folder)
    image_files = [f for f in files if f.endswith(".jpg") or f.endswith(".png")]
    
    # Shuffle the file names randomly
    random.shuffle(image_files)
    
    # Calculates the number of images for each set
    num_images = len(image_files)
    num_train = int(num_images * 0.8)
    num_val = int((num_images - num_train) / 2)
    
    # Divides the file names into three sets
    train_files = image_files[:num_train]
    val_files = image_files[num_train:num_train+num_val]
    test_files = image_files[num_train+num_val:]
    
    # Create a file for the train data
    with open(os.path.join(folder, "traindata.txt"), "w") as f:
        for image_file in train_files:
            f.write(os.path.join(folder, image_file) + "\n")
            print(os.path.join(folder, image_file) + "\n")
    
    # Create a file for valdidation data
    with open(os.path.join(folder, "valdata.txt"), "w") as f:
        for image_file in val_files:
            f.write(os.path.join(folder, image_file) + "\n")
            print(os.path.join(folder, image_file) + "\n")
    
    # Create a file for the test data
    with open(os.path.join(folder, "testdata.txt"), "w") as f:
        for image_file in test_files:
            f.write(os.path.join(folder, image_file) + "\n")
            print(os.path.join(folder, image_file) + "\n")
            
    # Create a file with all the dataset
    with open(os.path.join(folder, "train_dataset.txt"), "w") as f:
        for image_file in image_files:
                f.write(os.path.join(folder, image_file) + "\n")



# Function to distribute images and txt files to different folders from a .txt file
def split_data_for_training(txt_list, output_img_folder, output_txt_folder):
    # Create the output folder if it does not already exist
    os.makedirs(output_img_folder, exist_ok=True)
    os.makedirs(output_txt_folder, exist_ok=True)
    
    # Open the text file containing the image paths
    with open(txt_list, "r") as f:
        for line in f:
            image_path = line.strip()
            txt_file = os.path.splitext(os.path.basename(image_path))[0] + ".txt"
            
            # Move the image to the output folder
            shutil.move(image_path, os.path.join(output_img_folder, os.path.basename(image_path)))
            
            # Move the text file to the output folder
            shutil.move(os.path.join(os.path.dirname(image_path), txt_file), os.path.join(output_txt_folder, txt_file))

split_data_for_training('traindata.txt', 'images/train', 'labels/train')
split_data_for_training('valdata.txt', 'images/val', 'labels/val')
split_data_for_training('testdata.txt', 'images/test', 'labels/test')
