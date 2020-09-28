"""Unit tests for the image_sort module
"""
import os
import sys
import shutil

# pylint: disable=wrong-import-position
# pylint: disable=import-error

tests_path = os.path.dirname(os.path.abspath(__file__))
src_path = tests_path+'/../'
sys.path.insert(0, src_path)
from image_sort import ImageSort

ASSETS_PATH = tests_path+'/../../assets/test_assets/'
TEST_ASSETS = [os.path.join(ASSETS_PATH, asset) for asset in os.listdir(ASSETS_PATH)]

def test_find_images(tmp_path):
    """ Test that the tool can find the images in the test assets directory
    """
    # Convert posix path to string for older python versions
    tmp_path = str(tmp_path)

    # Copy test assets to a tmp_path
    src_assets = [shutil.copy2(asset, tmp_path) for asset in TEST_ASSETS]

    sorter = ImageSort(tmp_path, tmp_path, None)
    sorter.find_images()

    # Ensure finder found right number of images
    assert len(src_assets) == len(sorter.image_list)

    # Sort found images and compare to to the source list to ensure it is identical
    src_assets.sort()
    sorter.image_list.sort()
    assert all([src == found for src, found in zip(src_assets, sorter.image_list)])
    # Cleanup child threads
    sorter.cleanup()


def test_sort_images(tmp_path):
    """ Test that the tool can sort the images in the test assets directory
    """
    sorted_gt = ['failed_to_sort/no_exif.jpg',
                 '2013/04/20130407_132135.JPG',
                 '2013/04/20130408_131738.JPG']
    # Convert posix path to string for older python versions
    tmp_path = str(tmp_path)

    # Create tmp directories for the test
    tmp_src = os.path.join(tmp_path, 'src/')
    tmp_dst = os.path.join(tmp_path, 'dst/')
    os.mkdir(tmp_src)
    os.mkdir(tmp_dst)

    # Add the tmp directory to the ground truths
    sorted_gt = [os.path.join(tmp_dst, gt_path) for gt_path in sorted_gt]

    # Copy test assets to a tmp_path
    for asset in TEST_ASSETS:
        shutil.copy2(asset, tmp_src)
    sorter = ImageSort(tmp_src, tmp_dst, None)
    sorter.find_images()

    # Run the sorting
    sorter.run_parallel_sorting()

    # Find sorted images
    sorted_list = []
    for root_path, __, files in os.walk(tmp_dst):
        for file_name in files:
            sorted_list.append(os.path.join(root_path, file_name))

    # Check sorted images where sorted correctly
    sorted_list.sort()
    sorted_gt.sort()
    assert len(sorted_list) == len(sorted_gt)
    assert all([sort_path == gt_path for sort_path, gt_path in zip(sorted_list, sorted_gt)])
    # Cleanup child threads
    sorter.cleanup()