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
