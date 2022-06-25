import cv2 as cv
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import json
import pickle
from tqdm import tqdm
import math
from scipy.spatial import distance
from skimage import measure
import scipy.io as scio
import pycocotools.mask as mask_util


root = "data/osd"
instance_dir = os.path.join(root, "inst/")
image_dir = os.path.join(root, "img/")
txt_dir = root
label_dir = os.path.join(root, "annotations")


def read_txt(path, split='train'):
    txt_path = os.path.join(path, "{}.txt".format(split))
    with open(txt_path) as f:
        ids = f.readlines()
    return ids


def close_contour(contour):
    if not np.array_equal(contour[0], contour[-1]):
        contour = np.vstack((contour, contour[0]))
    return contour


def binary_mask_to_polygon(binary_mask, tolerance=0):
    polygons = []
    # pad mask to close contours of shapes which start and end at an edge
    padded_binary_mask = np.pad(binary_mask, pad_width=1, mode='constant', constant_values=0)
    contours = measure.find_contours(padded_binary_mask, 0.5)
    contours = np.subtract(contours, 1)
    for contour in contours:
        contour = close_contour(contour)
        contour = measure.approximate_polygon(contour, tolerance)
        if len(contour) < 3:
            continue
        contour = np.flip(contour, axis=1)
        segmentation = contour.ravel().tolist()
        # after padding and subtracting 1 we may get -0.5 points in our segmentation
        segmentation = [0 if i < 0 else i for i in segmentation]
        polygons.append(segmentation)
    return polygons


def generate_anno(inst_path, images_info, annotations, count, mode, N=128):
    # seg_cls_name = os.path.join(root, 'cls', inst_path.split('/')[-1])
    # seg_cls_mat = scio.loadmat(seg_cls_name)
    # semantic_mask = seg_cls_mat['GTcls']['Segmentation'][0][0]

    # seg_obj_mat = scio.loadmat(inst_path)
    seg_obj_mat = cv.imread(inst_path, 0)
    instance_mask = seg_obj_mat.copy()
    
    # instance_mask = seg_obj_mat['GTinst']['Segmentation'][0][0]

    instance_ids = np.unique(instance_mask)

    img_name = inst_path.split('/')[-1]

    imw = instance_mask.shape[1]
    imh = instance_mask.shape[0]

    has_object = False
    
    for instance_id in instance_ids:
        if instance_id == 0 or instance_id == 255:  # background or edge, pass
            continue

        # extract instance
        temp = np.zeros(instance_mask.shape)
        temp.fill(instance_id)

        tempMask = (instance_mask == temp)
        cat_id = np.max(np.unique(seg_obj_mat * tempMask))  # semantic category of this instance
        
        instance = instance_mask * tempMask
        instance_temp = instance.copy()  # findContours will change instance, so copy first
        if mode == 'mask':
            rle = mask_util.encode(np.array(instance, order='F'))
            rle['counts'] = rle['counts'].decode('utf-8')
            area = int(np.sum(tempMask))
            x, y, w, h = cv.boundingRect(instance_temp.astype(np.uint8))
            has_object = True
            count += 1
            anno = {'segmentation': rle, 'area': area,
                    'image_id': int(img_name[4:8]), 'bbox': [x, y, w, h],
                    'iscrowd': 0, 'category_id': int(cat_id), 'id': count}

            
        else:
            polys = binary_mask_to_polygon(instance)
            if len(polys) == 0:
                continue
            area = int(np.sum(tempMask))
            x, y, w, h = cv.boundingRect(instance_temp.astype(np.uint8))
            has_object = True
            count += 1
            anno = {'segmentation': polys, 'area': area,
                    'image_id': int(img_name[4:8]), 'bbox': [x, y, w, h],
                    'iscrowd': 0, 'category_id': int(cat_id), 'id': count}



        annotations.append(anno)

    if has_object == True:
        info = {'file_name': img_name.replace('png', 'jpg'),
                'height': imh, 'width': imw, 'id': int(img_name[4:8])}
        images_info.append(info)

    return images_info, annotations, count


def save_annotations(ann, path, split='train'):
    os.system('mkdir -p {}'.format(path))
    instance_path = os.path.join(path, "osd_{}_instance.json".format(split))
    with open(instance_path, 'w') as f:
        json.dump(ann, f)


categories = [
    {'supercategory': 'none', 'id': 0, 'name': 'sea-surface'},
    {'supercategory': 'none', 'id': 1, 'name': 'oil-spill'},
    {'supercategory': 'none', 'id': 2, 'name': 'look-alike'},
    {'supercategory': 'none', 'id': 3, 'name': 'ship'},
    {'supercategory': 'none', 'id': 4, 'name': 'land'}
]


def convert_labels(ids, split, mode):
    images = []
    annotations = []
    label_save_dir = label_dir
    count = 0
    for i in tqdm(range(len(ids))):
        inst_path = os.path.join(instance_dir, ids[i][:-1] + '.png')
        images, annotations, count = generate_anno(inst_path, images, annotations, count, mode)
    voc_instance = {'images': images, 'annotations': annotations, 'categories': categories}
    save_annotations(voc_instance, label_save_dir, split=split)


def convert_osd():
    ids_train_noval = read_txt(txt_dir, 'train_noval')

    ids_train = read_txt(txt_dir, 'train')
    ids_val = read_txt(txt_dir, 'val')

    ids_val5732 = []

    for id in ids_train+ids_val:
        if id not in ids_train_noval:
            ids_val5732.append(id)

    ids_val5732 = list(set(ids_val5732))
    convert_labels(ids_train_noval, 'train', 'snake')
    convert_labels(ids_val5732, 'trainval', 'snake')
    convert_labels(ids_val5732, 'val', 'mask')


if __name__ == '__main__':
    convert_osd()

