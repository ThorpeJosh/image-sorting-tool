from setuptools import setup
from image_sorting_tool import __version__ as version

setup(
    name='image-sorting-tool',
    version=version,
    url='https://github.com/ThorpeJosh/image-sorting-tool',
    license='MIT',
    author='Joshua Thorpe',
    author_email='josh@thorpe.engineering',
    description='Graphical tool to sort images into a folder structure based on the date the images were taken',
    long_description=''.join(open('README.md', encoding='utf-8').readlines()),
    long_description_content_type='text/markdown',
    keywords=['image', 'sort', 'gui', 'executable'],
    packages=['image_sorting_tool'],
    include_package_data=True,
    install_requires=['Pillow>=6.0.0', 'python-dateutil>=2.8.0'],
    extras_require = {"dev": ["pytest>=6.0.0", "pylint>=2.0.0", "tox>= 3.0.0"]},
    python_requires='>=3.5',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS'
    ],
    entry_points={
        'gui_scripts': [
            'image-sorting-tool=image_sorting_tool.__main__:run'
        ],
    },
)
