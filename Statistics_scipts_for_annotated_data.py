import os
import re
import codecs

"""
Marion Charpier
---
This script was produced as part of an M2 TNAH internship at the École des Chartes,
under the joint supervision of the University of Humboldt (Berlin) and the IRHT-CNRS (Paris).
---
"""


"""
Distribution des sources annotées
"""

#Fonction pour récupérer tous les fichiers images
def get_image_files(folder):
    image_extensions = (".jpg", ".jpeg", ".png", ".gif")
    image_files = [filename for filename in os.listdir(folder) if filename.endswith(image_extensions)]
    return image_files

#Fonctions pour compter le nombre de manuscrits dont sont issues les images
def nb_manuscripts(folder):
    # Images à parcourir
    image_files = get_image_files(folder)
    # print(image_files)

    idno = re.compile(r'^(.+)_\d+\.(jpg|jpeg|png)$')

    # Liste pour stocker les noms de fichiers
    noms_fichiers = []

    # Parcours des fichiers du répertoire
    for nom_fichier in image_files:
        match = idno.match(nom_fichier)
        if match:
            ms_name = match.group(1)
            noms_fichiers.append(ms_name)

    # Suppression des doublons
    noms_fichiers_sans_doublons = list(set(noms_fichiers))

    nombre_ms = len(noms_fichiers_sans_doublons)
    print(nombre_ms)


#Fonction pour compter le nombre d'images retenues par manuscrit
def occurences(folder):
    # Images à parcourir
    image_files = get_image_files(folder)

    idno = re.compile(r'^(.+)_\d+\.(jpg|jpeg|png)$')

    # Liste pour stocker les noms de fichiers
    noms_fichiers = []

    # Parcours des fichiers du répertoire
    for nom_fichier in image_files:
        match = idno.match(nom_fichier)
        if match:
            ms_name = match.group(1)
            noms_fichiers.append(ms_name)
    # Comptage des occurrences
    occurrences = {}
    for nom in noms_fichiers:
        if nom not in occurrences:
            occurrences[nom] = noms_fichiers.count(nom)

    # Tri des résultats par nombre décroissant
    resultats_tries = sorted(occurrences.items(), key=lambda x: x[1], reverse=True)

    # Affichage des résultats
    for ms_name, nb_occurrences in resultats_tries:
        print(f"{ms_name}: {nb_occurrences}")



"""
Distribution des annotations
"""

#Fonction pour récupérer les fichiers d'annotations
def get_annotation_files(folder):
    image_extensions = (".jpg", ".jpeg", ".png", ".gif")
    image_files = [filename for filename in os.listdir(folder) if filename.endswith(image_extensions)]
    annotation_files = []
    
    for image_file in image_files:
        image_name, image_ext = os.path.splitext(image_file)
        annotation_file = f"{image_name}.txt"
        if os.path.isfile(os.path.join(folder, annotation_file)):
            annotation_files.append(annotation_file)

    return annotation_files
    # print(annotation_files)



#Fonction pour vérifier que tous les fichiers d'annotations sont bien encodés en utf-8
def encoding(folder):
    
    annotations_txt = get_annotation_files(folder)

    for filename in annotations_txt:
        file_path = os.path.join(folder, filename)
        with open(file_path, 'rb') as f:
            rawdata = f.read()
        try:
            result = codecs.decode(rawdata, 'utf-8')
        except UnicodeDecodeError:
            try:
                result = codecs.decode(rawdata, 'iso-8859-1')
                print(f"{filename} is encoded in ISO-8859-1")
            except UnicodeDecodeError:
                print(f"{filename} encoding not recognized")


#Fonction pour récupérer le nombre d'images sans annotations                
def img_without_annotations(folder):
    annotation_files = get_annotation_files(folder)
    
    count = 0
    for annotation_file in annotation_files:
        with open(os.path.join(folder, annotation_file), 'r') as f:
            annotations = f.read()
            if annotations == "":
                count += 1
                print(f"Le fichier {annotation_file} est vide.")

    print(count)
    

#Fonction pour récupérer le nombre d'annotations par image
def annotations_per_img(folder):
    annotation_files = get_annotation_files(folder)
    
    nb_lignes_par_fichier = {}

    for annotation_file in annotation_files:
        with open(os.path.join(folder, annotation_file), 'r') as f:
            nb_lignes = 0
            for ligne in f:
                nb_lignes += 1

        nb_lignes_par_fichier[annotation_file] = nb_lignes

    nb_lignes_par_fichier_tries = dict(sorted(nb_lignes_par_fichier.items(), key=lambda x: x[1], reverse=True))

    with open("Statistics/annotations_per_img.txt", "w") as resultat_file:
        for annotation_file, nb_lignes in nb_lignes_par_fichier_tries.items():
            resultat_file.write(f"Le fichier {annotation_file} contient {nb_lignes} lignes.\n")
        
    # print(f"Le fichier {annotation_file} contient {nb_lignes} lignes.")


#Fonction pour récupérer le nombre total d'annotations
def total_annotations(folder):
    annotation_files = get_annotation_files(folder)

    total_lignes = 0

    for annotation_file in annotation_files:
        with open(os.path.join(folder, annotation_file), 'r') as f:
            nb_lignes = 0
            for ligne in f:
                if ligne.strip():  # ignore les lignes vides
                    nb_lignes += 1
            total_lignes += nb_lignes

    print(f"Le total des annotations est {total_lignes}.")


#Fonction pour récupérer le nombre d'annotations en fonction des différentes classes
def annotations_classes(folder):

    annotation_files = get_annotation_files(folder)

    occurences = {}
    for annotation_file in annotation_files:
        with open(os.path.join(folder, annotation_file), 'r', encoding='ascii') as f:
            for ligne in f:
                coa_code = ligne.split()[0]
                if coa_code not in occurences:
                    occurences[coa_code] = 1
                else:
                    occurences[coa_code] += 1
    
    for coa_code, nb_occurences in occurences.items():
        print(f"{coa_code} : {nb_occurences} occurences")
