"""Unit tests for the image_sort module
"""
import os
import sys
import shutil
import pytest

# pylint: disable=wrong-import-position
# pylint: disable=import-error

tests_path = os.path.dirname(os.path.abspath(__file__))
src_path = tests_path + "/../"
sys.path.insert(0, src_path)
from image_sort import ImageSort
from image_sort import JPEG_EXTENSIONS

ASSETS_PATH = tests_path + "/../../assets/test_assets/"
TEST_ASSETS = [os.path.join(ASSETS_PATH, asset) for asset in os.listdir(ASSETS_PATH)]


@pytest.mark.parametrize(
    "test_extensions,expected_found",
    [
        (
            JPEG_EXTENSIONS,
            ["no_exif.jpg", "no_exif20000101-010101.jpg", "pass_0.JPG", "pass_1.JPG"],
        ),
        ([".png"], ["Screenshot 2017-05-12 18.46.55.png"]),
        ([".mp4"], ["20180930_165600.mp4"]),
        ([".gif"], ["Animated_2018-0305_093556.gif"]),
        (
            JPEG_EXTENSIONS + [".png", ".mp4", ".gif"],
            [
                "no_exif.jpg",
                "no_exif20000101-010101.jpg",
                "pass_0.JPG",
                "pass_1.JPG",
                "Animated_2018-0305_093556.gif",
                "20180930_165600.mp4",
                "Screenshot 2017-05-12 18.46.55.png",
            ],
        ),
    ],
)  # Tests each filetype indiviually and then collectively
def test_find_images(tmp_path, test_extensions, expected_found):
    """Test that the tool can find the images in the test assets directory"""
    # Convert posix path to string for older python versions
    tmp_path = str(tmp_path)

    # Copy test assets to a tmp_path
    for asset in TEST_ASSETS:
        shutil.copy2(asset, tmp_path)

    # Run finding tool
    sorter = ImageSort(tmp_path, tmp_path, None)
    sorter.ext_to_sort = test_extensions
    sorter.find_images()

    # Ensure finder found right number of images
    assert len(expected_found) == len(sorter.sort_list)

    # Sort found images and compare to to the source list to ensure it is identical
    expected_found.sort()
    sort_list = [image[0] for image in sorter.sort_list]
    sort_list.sort()

    # Add the tmp_path to the expected found list
    expected_found = [os.path.join(tmp_path, filepath) for filepath in expected_found]

    print(f"Expected to be found : {expected_found}")
    print(f"Sort list : {sorter.sort_list}")
    assert all(expected == found for expected, found in zip(expected_found, sort_list))
    # Cleanup child threads
    sorter.cleanup()


@pytest.mark.parametrize(
    "test_extensions,expected_sort",
    [
        (
            JPEG_EXTENSIONS,
            [
                "failed_to_sort/no_exif.jpg",
                "2000/01/20000101_010101.jpg",
                "2013/04/20130407_132135.JPG",
                "2013/04/20130408_131738.JPG",
            ],
        ),
        ([".png"], ["2017/05/20170512_184655.png"]),
        ([".mp4"], ["2018/09/20180930_165600.mp4"]),
        ([".gif"], ["2018/03/20180305_093556.gif"]),
        (
            JPEG_EXTENSIONS + [".png", ".mp4", ".gif"],
            [
                "failed_to_sort/no_exif.jpg",
                "2013/04/20130407_132135.JPG",
                "2013/04/20130408_131738.JPG",
                "2000/01/20000101_010101.jpg",
                "2018/03/20180305_093556.gif",
                "2018/09/20180930_165600.mp4",
                "2017/05/20170512_184655.png",
            ],
        ),
    ],
)  # Tests each filetype indiviually and then collectively
def test_sort_images(tmp_path, test_extensions, expected_sort):
    """Test that the tool can sort the images in the test assets directory"""
    # Convert posix path to string for older python versions
    tmp_path = str(tmp_path)

    # Create tmp directories for the test
    tmp_src = os.path.abspath(os.path.join(tmp_path, "src/"))
    tmp_dst = os.path.abspath(os.path.join(tmp_path, "dst/"))
    os.mkdir(tmp_src)
    os.mkdir(tmp_dst)

    # Add the tmp directory to the ground truths
    sorted_gt = [
        os.path.abspath(os.path.join(tmp_dst, gt_path)) for gt_path in expected_sort
    ]

    # Copy test assets to a tmp_path
    for asset in TEST_ASSETS:
        shutil.copy2(asset, tmp_src)
    sorter = ImageSort(tmp_src, tmp_dst, None)
    sorter.ext_to_sort = test_extensions
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
    assert all(
        sort_path == gt_path for sort_path, gt_path in zip(sorted_list, sorted_gt)
    )
    # Cleanup child threads
    sorter.cleanup()


@pytest.mark.parametrize(
    "test_extensions",
    [
        (JPEG_EXTENSIONS),
        ([".png"]),
        ([".mp4"]),
        ([".gif"]),
        (JPEG_EXTENSIONS + [".png", ".mp4", ".gif"]),
    ],
)
def test_find_other_files(tmp_path, test_extensions):
    """Test that the tool can find unsorted files in the test assets directory"""
    # Convert posix path to string for older python versions
    tmp_path = str(tmp_path)

    # Copy test assets to a tmp_path
    tmp_assets = [shutil.copy2(asset, tmp_path) for asset in TEST_ASSETS]

    # Run finding tool
    sorter = ImageSort(tmp_path, tmp_path, None)
    sorter.ext_to_sort = test_extensions
    sorter.find_images()

    # Adjust the assets list for only unsortable files
    unsorted_assets = []
    for asset in tmp_assets:
        if not asset.lower().endswith(tuple(test_extensions)):
            unsorted_assets.append(asset)

    # Ensure finder found right number of images
    assert len(unsorted_assets) == len(sorter.other_list)

    # Sort found images and compare to to the source list to ensure it is identical
    unsorted_assets.sort()
    sorter.other_list.sort()
    assert all(src == found for src, found in zip(unsorted_assets, sorter.other_list))
    # Cleanup child threads
    sorter.cleanup()


@pytest.mark.parametrize(
    "test_extensions,expected_result",
    [
        (
            JPEG_EXTENSIONS,
            [
                "failed_to_sort/no_exif.jpg",
                "2000/01/20000101_010101.jpg",
                "2013/04/20130407_132135.JPG",
                "2013/04/20130408_131738.JPG",
                "other_files/text.txt",
                "other_files/Screenshot 2017-05-12 18.46.55.png",
                "other_files/20180930_165600.mp4",
                "other_files/Animated_2018-0305_093556.gif",
            ],
        ),
        (
            [".png"],
            [
                "other_files/no_exif.jpg",
                "other_files/no_exif20000101-010101.jpg",
                "other_files/pass_0.JPG",
                "other_files/pass_1.JPG",
                "2017/05/20170512_184655.png",
                "other_files/text.txt",
                "other_files/20180930_165600.mp4",
                "other_files/Animated_2018-0305_093556.gif",
            ],
        ),
        (
            [".mp4"],
            [
                "other_files/no_exif.jpg",
                "other_files/no_exif20000101-010101.jpg",
                "other_files/pass_0.JPG",
                "other_files/pass_1.JPG",
                "other_files/Screenshot 2017-05-12 18.46.55.png",
                "other_files/text.txt",
                "2018/09/20180930_165600.mp4",
                "other_files/Animated_2018-0305_093556.gif",
            ],
        ),
        (
            [".gif"],
            [
                "other_files/no_exif.jpg",
                "other_files/no_exif20000101-010101.jpg",
                "other_files/pass_0.JPG",
                "other_files/pass_1.JPG",
                "other_files/Screenshot 2017-05-12 18.46.55.png",
                "other_files/text.txt",
                "other_files/20180930_165600.mp4",
                "2018/03/20180305_093556.gif",
            ],
        ),
        (
            JPEG_EXTENSIONS + [".png", ".mp4", ".gif"],
            [
                "failed_to_sort/no_exif.jpg",
                "2013/04/20130407_132135.JPG",
                "2013/04/20130408_131738.JPG",
                "2000/01/20000101_010101.jpg",
                "2018/03/20180305_093556.gif",
                "2018/09/20180930_165600.mp4",
                "other_files/text.txt",
                "2017/05/20170512_184655.png",
            ],
        ),
    ],
)  # Tests each filetype indiviually and then collectively
def test_copy_images(tmp_path, test_extensions, expected_result):
    """Test that the tool can copy the unsorted files in the test assets directory
    when the user selects this option.
    """
    # Convert posix path to string for older python versions
    tmp_path = str(tmp_path)

    # Create tmp directories for the test
    tmp_src = os.path.abspath(os.path.join(tmp_path, "src/"))
    tmp_dst = os.path.abspath(os.path.join(tmp_path, "dst/"))
    os.mkdir(tmp_src)
    os.mkdir(tmp_dst)

    # Add the tmp directory to the ground truths
    expected_result = [
        os.path.abspath(os.path.join(tmp_dst, path)) for path in expected_result
    ]

    # Copy test assets to a tmp_path
    for asset in TEST_ASSETS:
        shutil.copy2(asset, tmp_src)
    sorter = ImageSort(tmp_src, tmp_dst, None)
    sorter.ext_to_sort = test_extensions
    # Enable the copy feature
    sorter.copy_unsorted = True
    sorter.find_images()

    # Run the copy process
    sorter.run_parallel_sorting()

    # Find sorted files
    sorted_list = []
    for root_path, __, files in os.walk(tmp_dst):
        for file_name in files:
            sorted_list.append(os.path.join(root_path, file_name))

    # Check unsortable files were copied correctly
    sorted_list.sort()
    expected_result.sort()
    assert len(sorted_list) == len(expected_result)
    print(f"sorted_list : {sorted_list}")
    print(f"expected result : {expected_result}")
    for result, exp_result in zip(sorted_list, expected_result):
        print(result, exp_result)
    assert all(
        sort_path == gt_path for sort_path, gt_path in zip(sorted_list, expected_result)
    )
    # Cleanup child threads
    sorter.cleanup()
