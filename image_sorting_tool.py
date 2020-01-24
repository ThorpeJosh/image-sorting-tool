""" Simple sorting program that finds all images in the SRC_DIR and copies them to the DST_DIR, whilst putting them in the correct folder structure and renaming the filenames"""
import os
import shutil
from multiprocessing import Pool
from datetime import datetime
from PIL import Image

THREAD_COUNT=8
SRC_DIR = '/mnt/c/Users/Caroline/OneDrive/Pictures/CameraRoll/'
DST_DIR = '/mnt/c/Users/Caroline/OneDrive/Pictures/sorted_images/'

file_list = []
for root, dirs, files in os.walk(SRC_DIR):
    for file_name in files:
        file_list.append(os.path.join(root, file_name))

image_list = []
for f in file_list:
    if f.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_list.append(f)

def sort_image(image_path):
    try:
        date_taken = Image.open(image_path)._getexif()[36867]
        dt= datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
        new_name = '{}{}{}_{}{}{}{}'.format(dt.year.zfill(4), dt.month.zfill(2), dt.day.zfill(2), dt.hour.zfill(2), dt.minute.zfill(2), dt.second.zfill(2), os.path.splitext(image_path)[1])
        new_path = os.path.join(DST_DIR, str(dt.year).zfill(4), str(dt.month).zfill(2))
        os.makedirs(new_path, exist_ok=True)
        shutil.copyfile(image_path, os.path.join(new_path, new_name))
        print('Sorted: {}'.format(image_path))
    except:
        new_path = os.path.join(DST_DIR, 'failed_to_sort')
        new_name = os.path.split(image_path)[1]
        os.makedirs(new_path, exist_ok=True)
        shutil.copyfile(image_path, os.path.join(new_path, new_name))
        print('Failed: {}'.format(image_path))


total_images = len(image_list)
print("Found {} files, {} are images".format(len(file_list), total_images))
    
with Pool(processes=THREAD_COUNT) as pool:
    pool.map(sort_image, image_list)


