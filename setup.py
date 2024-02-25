import os
import re
from setuptools import setup
from setuptools.command.install import install
from py7zip.general import get_version
from py7zip import py7zip

__name__ = 'py7zip'
__author__ = 'AliasfoxKDE'
__description__ = "An unofficial, cross platform, lightweight, and easy to use wrapper for 7zip command line binaries (7za) in Python. "
__version__ = get_version()

project_urls = {
    'Homepage': f'https://pypi.org/project/{__name__}',
    'Source Code': f'https://github.com/{__author__}/{__name__}',
    'Documentation': f'https://github.com/{__author__}/{__name__}/blob/main/README.md',
    'Project Page': f'https://{__name__}.cyopsys.com'
}

with open("README.md", "r") as rm:
    long_description = rm.read()

def install():
    py7zip.Py7zip()
   
setup(
    name=__name__,
    packages=[__name__],
    version=__version__,
    license='MIT',
    author=__author__,
    author_email=f"{__author__}@gmail.com",
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=project_urls['Source Code'],
    project_urls=project_urls,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'py7zip-setup = py7zip.py7zip:setup'
        ]
    },
    cmdclass={
        'install': install(),
    },
    include_package_data=True,
    package_data={'': [
        'README.md'
    ]},
)