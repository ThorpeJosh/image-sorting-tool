# Image Sorting Tool
[![Python Checks](https://github.com/ThorpeJosh/image-sorting-tool/actions/workflows/python-test.yml/badge.svg)](https://github.com/ThorpeJosh/image-sorting-tool/actions/workflows/python-test.yml)
[![PyPI version](https://img.shields.io/pypi/v/image-sorting-tool.svg)](https://pypi.org/project/image-sorting-tool/)
[![PyPI version](https://img.shields.io/pypi/pyversions/image-sorting-tool.svg)](https://pypi.org/project/image-sorting-tool/)
[![PyPI license](https://img.shields.io/pypi/l/image-sorting-tool.svg)](https://pypi.org/project/image-sorting-tool/)  
![Screenshot](https://raw.githubusercontent.com/ThorpeJosh/image-sorting-tool/main/assets/ImageSortingTool.png)
This is a simple graphical tool to sort media into a structured folder. It is designed primarily for JPG images taken with a camera/phone but will also work with MP4, PNG and GIF media files. It works by finding all files in a chosen source directory (including sub-directories) and then based on the chosen sorting options, copies them into a structured destination.

The date-taken for JPG files is extracted from the EXIF data and for all other file formats the filename is used to extract the date-taken. The files destination name will be in format 'yyyymmdd_HHMMSS'. For example '20201225_234532.jpg'
The default output structure is year and month folders. For example:

/<br>
├── 2019/<br>
&ensp;&ensp;&ensp;&ensp;├── 07/<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;├── 20190712_141507.jpg<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;└── 20190719_224521.jpg<br>
&ensp;&ensp;&ensp;&ensp;└── 10/<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;├── 20191011_180520.jpg<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;└── 20191029_204731.jpg<br>
└── 2020/<br>
&ensp;&ensp;&ensp;&ensp;├── 01/<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;└── 20200114_135312.jpg<br>
&ensp;&ensp;&ensp;&ensp;└── 03/<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;└── 20200301_110330.jpg<br>

Files that cannot have the date-taken extracted (missing EXIF or bad filenames) will be copied to a 'failed_to_sort' folder in the root directory of the above structure without any renaming. These files are commonly ones downloaded from the internet or shared through social media.

If your source folder has other files such as binaries, documents, audio recordings, or music, you can choose if you want to ignore them or copy them to an 'other_files' folder with the 'Copy all other files' option.

This tool is multi-threaded to increase performance on high speed storage such as SSDs.

No data in the source directory is altered. It only reads from the source, and then copy operations are performed during the sorting process.

## Installation
The tool can be run on Linux, MacOS and Windows provided the following requirements are met
### Requirements
* [Python](https://www.python.org/downloads/) (compatible versions are listed at top of readme)
* python3-tk (Comes with Python 3, but may need installing separately in linux)
* [pipx](https://pipx.pypa.io/) (highly recommended, but `pip` will also work)

It is recommended to install `image-sorting-tool` with `pipx` as it will manage a dedicated environment and all paths for you, eliminating risk of dependency conflicts, etc.

To install run the following
```shell
pipx install image-sorting-tool
```

## Usage
Run the following to launch
```bash
image-sorting-tool
```
## Upgrading
Run the following to upgrade
```bash
pipx upgrade image-sorting-tool
```
## Uninstalling
Run the following to remove the tool from your machine
```bash
pipx uninstall image-sorting-tool
```

## Development
To contribute, clone this repo and then install the dev dependencies with
```shell
# Installs package locally so code changes will affect behaviour
pip install -e .[dev]

#Launch with -vv flag for debug logs
image-sorting-tool -vv 
```

### Automated checks
Linting and unit tests should be checked before committing by running the following:
```bash
# Code formatting
black  image-sorting-tool

# Linting
pylint image_sorting_tool

# Unit test on current environment python version
pytest
```
