"""
Marion Charpier
---
This script was produced as part of an M2 TNAH internship at the École des Chartes,
under the joint supervision of the University of Humboldt (Berlin) and the IRHT-CNRS (Paris).
---
"""

import os
import glob


"""
Le code la fonction 'calculate_iou' est adapté de la fonction 'bb_intersection_over_union' issue de https://pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/
L'adaptation a été nécessaire car 'bb_intersection_over_union' les coordonnées utilisées sont données en x_min, y_min, x_max, y_max).
Or, les coordonnées issues de YOLOv7 pour chaque annotation sont relatives et données en x, y, w, h.
"""


def calculate_iou(box1, box2):
    # Convertir les coordonnées (x, y, w, h) en coordonnées (x_min, y_min, x_max, y_max)
    box1_x_min = box1[1] - box1[3] / 2
    box1_y_min = box1[2] - box1[4] / 2
    box1_x_max = box1[1] + box1[3] / 2
    box1_y_max = box1[2] + box1[4] / 2
    
    box2_x_min = box2[1] - box2[3] / 2
    box2_y_min = box2[2] - box2[4] / 2
    box2_x_max = box2[1] + box2[3] / 2
    box2_y_max = box2[2] + box2[4] / 2
    
    # Calculer les coordonnées (x,y) de l'intersection
    x_min = max(box1_x_min, box2_x_min)
    y_min = max(box1_y_min, box2_y_min)
    x_max = min(box1_x_max, box2_x_max)
    y_max = min(box1_y_max, box2_y_max)
    
    # Calculer l'aire de l'intersection
    intersection_area = max(0, x_max - x_min + 1) * max(0, y_max - y_min + 1)

    # Calculer l'aire des deux bounding boxes
    box1_area = (box1_x_max - box1_x_min + 1) * (box1_y_max - box1_y_min + 1)
    box2_area = (box2_x_max - box2_x_min + 1) * (box2_y_max - box2_y_min + 1)
    
    # Calculer l'Intersection over Union (IoU)
    iou = intersection_area / float(box1_area + box2_area - intersection_area)
    
    return iou


"""
La fonction match_boxes permet de retourner les bbxes annotées et leur correspondance prédite.
Cette fonction permet également de retourner les faux positifs (objet prédits alors qu'il n'y pas d'équivalent dans la vérité terrain) et 
les faux négatifs (objets présents dans la vérité terrain mais non détectés).
La fonction prend en compte trois paramètres : les coordonnées d'annotations, les coordonnées de prédictions et le seuil de prédiction,
c'est à dire seuil en-dessous duquel l'objet détecté sera considéré comme un faux négatifs (si issu de la vérité terrain) ou comme
faux positifs (si issu de prédiction).
Ce dernier 'threshold' est par défaut implémenter à 0.50, ce qui correspond aux recommandations du PASCAL VOC challenge ou à à 0.75 (détection strict) :
https://cocodataset.org/?ref=jeremyjordan.me#detection-eval.
Avec un 'threshold' à 0.1 les erreurs de localisation sont ignorées.
 """

def match_boxes(annotations, predictions, threshold):
    matched_annotations = []
    matched_predictions = []

    for annotation in annotations:
        annotation_box = annotation.split(" ")
        annotation_box = [float(coord) for coord in annotation_box]
        annotation_class = int(annotation_box[0])

        best_iou = 0
        best_prediction_idx = -1

        for i, prediction in enumerate(predictions):
            prediction_box = prediction.split(" ")
            prediction_box = [float(coord) for coord in prediction_box]
            prediction_class = int(prediction_box[0])

            if  annotation_class == prediction_class:
                iou = calculate_iou(annotation_box, prediction_box)

                if iou > best_iou and iou >= threshold:
                    best_iou = iou
                    best_prediction_idx = i

        if best_prediction_idx != -1:
            matched_annotations.append(annotation)
            matched_predictions.append(predictions[best_prediction_idx])

    false_positives = [p for p in predictions if p not in matched_predictions]
    false_negatives = [a for a in annotations if a not in matched_annotations]

    return matched_annotations, matched_predictions, false_positives, false_negatives


def load_data_from_files(file_paths):
    data_list = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data_list.append(line.strip())
    return data_list

directory_results = ''
output_file = os.path.join(directory_results,'results_for_graphics.csv')   # Nom du fichier de sortie

# Get annotation files
img_ann_dir = os.path.join(directory_results, 'labels_ann')
ann_files = glob.glob(os.path.join(img_ann_dir, '*.txt'))
annotations = load_data_from_files(ann_files)

# Get prediction files
img_pred_dir = os.path.join(directory_results, 'labels_pred')
pred_files = glob.glob(os.path.join(img_pred_dir, '*.txt'))
predictions = load_data_from_files(pred_files)

with open(output_file, 'w', newline='') as csvfile:
    fieldnames = ['Filename', 'Box_coordinates', 'TP/FP/FN', 'classe', 'Matched_boxes', 'IoU']  # Ajout des nouvelles colonnes
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for ann_file in ann_files:
        ann_file_name = os.path.basename(ann_file)
        matching_pred_files = [pred_file for pred_file in pred_files if os.path.basename(pred_file) == ann_file_name]
        if len(matching_pred_files) > 0:
            annotations = load_data_from_files([ann_file])
            predictions = load_data_from_files(matching_pred_files)

            matched_annotations, matched_predictions, false_positives, false_negatives = match_boxes(annotations, predictions, threshold=0.5)

            for annotation, prediction in zip(matched_annotations, matched_predictions):
                iou = calculate_iou([float(coord) for coord in annotation.split(" ")], [float(coord) for coord in prediction.split(" ")])
                box_coordinates = ' '.join(annotation.split(" "))

                writer.writerow({'Filename': os.path.basename(ann_file), 'Box_coordinates': box_coordinates, 'TP/FP/FN': 'TP', 'classe': get_class_name(annotation[0]), 'Matched_boxes': prediction, 'IoU': iou})

            if len(false_positives) != 0:
                for false_positive in false_positives:
                    writer.writerow({'Filename': os.path.basename(ann_file), 'Box_coordinates': false_positive, 'TP/FP/FN': 'FP', 'classe': get_class_name(false_positive[0]), 'Matched_boxes': '', 'IoU': ''})

            if len(false_negatives) != 0:
                for false_negative in false_negatives:
                    writer.writerow({'Filename': os.path.basename(ann_file), 'Box_coordinates': false_negative, 'TP/FP/FN': 'FN', 'classe': get_class_name(false_negative[0]), 'Matched_boxes': '', 'IoU': ''})



# Afficher un message lorsque l'écriture dans le fichier est terminée
print("Les résultats ont été enregistrés dans le fichier", output_file)
