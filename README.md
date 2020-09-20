# Image Sorting Tool
[![Build Status](http://jenkins.thorpe.engineering:8080/buildStatus/icon?job=image-sorting-tool%2Fmaster&subject=build%20status)](http://jenkins.thorpe.engineering:8080/job/ImageSortingTool/job/master/)  
![Screenshot](https://github.com/ThorpeJosh/ImageSortingTool/blob/master/assets/ImageSortingTool.PNG?raw=true)
This is a simple python tool that will find all the images in a source directory (including sub-directories) and copy them into a structured destination.

The date taken for each image will be extracted from the exif data and the image destination name will be by default in format 'yyyymmdd-HHMMSS'. For example '20201225-234532.jpg'
The default output structure is for sorted images to be placed in year and month folders. For example:

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

Images that do not have EXIF data available will be copied to a 'failed' folder in the root directory of the above directory structure without any renaming.

This tool is multithreaded to increase performance on high speed storage such as SSDs.

No data in the source directory is altered. It is only read from and then copy operations are performed during the sorting process.

## Installation

The tool can be run on Linux, MacOS and Windows provided the following requirements are met
### Requirements
* [Python 3](https://www.python.org/downloads/)
* python3-tk (Comes with Python 3, but may need installing seperately in linux)
* [PILLOW](https://pypi.org/project/Pillow/)

## Usage
From the root directory of this repository run
```python
python -m image_sorting_tool
```

## Development
To contribute, install the dev dependencies with
```python
pip install -e .[dev]
```

## Precompiled Downloads
Coming soon ....
