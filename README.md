# Image Sorting Tool
[![Build Status](https://jenkins.thorpe.work/buildStatus/icon?job=image-sorting-tool%2Fmaster&subject=build%20status)](https://jenkins.thorpe.work/blue/organizations/jenkins/image-sorting-tool/activity)
[![PyPI version](https://img.shields.io/pypi/v/image-sorting-tool.svg)](https://pypi.org/project/image-sorting-tool/)
[![PyPI license](https://img.shields.io/pypi/l/image-sorting-tool.svg)](https://pypi.org/project/image-sorting-tool/)  
![Screenshot](https://github.com/ThorpeJosh/ImageSortingTool/blob/master/assets/ImageSortingTool.PNG?raw=true)
This is a simple graphical tool to sort media into a scructured folder. It is designed primarily for JPG images taken with a camera/phone but will also work with MP4, PNG and GIF media files. It works by finding all files in a chosen source directory (including sub-directories) and then based on the chosen sorting options, copies them into a structured destination.

The date taken for JPG files will be extracted from the EXIF data and for all other file formats the filename will be used to extract the date taken. The files destination name will be in format 'yyyymmdd-HHMMSS'. For example '20201225-234532.jpg'
The default output structure is year and month folders. For example:

/<br>
├── 2019/<br>
&ensp;&ensp;&ensp;&ensp;├── 07/<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;├── 20190712-141507.jpg<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;└── 20190719-224521.jpg<br>
&ensp;&ensp;&ensp;&ensp;└── 10/<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;├── 20191011-180520.jpg<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;└── 20191029-204731.jpg<br>
└── 2020/<br>
&ensp;&ensp;&ensp;&ensp;├── 01/<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;└── 20200114-135312.jpg<br>
&ensp;&ensp;&ensp;&ensp;└── 03/<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;└── 20200301-110330.jpg<br>

Files that cannot have the date taken extracted (missing EXIF or bad filenames) will be copied to a 'failed_to_sort' folder in the root directory of the above structure without any renaming. These files are commonly ones downloaded from the internet or shared through social media.

If your source folder has other files such as binaries, documents, audio recordings, or music, you can choose if you want to ignore them or copy them to an 'other_files' folder with the 'Copy all other files' option.

This tool is multithreaded to increase performance on high speed storage such as SSDs.

No data in the source directory is altered. It only reads from the source, and then copy operations are performed during the sorting process.

## Installation
The tool can be run on Linux, MacOS and Windows provided the following requirements are met
### Requirements
* [Python 3.5](https://www.python.org/downloads/) or above
* python3-tk (Comes with Python 3, but may need installing seperately in linux)

To check what version of python is installed, open a console and run:
```bash
python --version
```
If the python version is suitable then run the following to install the image-sorting-tool
```bash
pip install image-sorting-tool
```

## Usage
Run the following to launch
```bash
image-sorting-tool
```
## Upgrading
Run the following to upgrade
```bash
pip install --upgrade image-sorting-tool
```

## Uninstalling
Run the following to remove the tool from your machine
```bash
pip uninstall image-sorting-tool
```

## Development
To contribute, clone this repo and then install the dev dependencies with
```bash
pip install .[dev]
```
### Automated checks
Linting and unit tests should be checked before commiting by running the following:
```bash
# Linting
pylint image_sorting_tool/*.py
pylint image_sorting_tool/tests/*.py

# Unit test on multiple python versions
tox
# Unit test on current environment python version
pytest
```
