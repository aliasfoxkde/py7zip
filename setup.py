import os
import re
from setuptools import setup

__name__ = 'py7zip'
__author__ = 'AliasfoxKDE'
__description__ = "An unofficial, cross-platform, lightweight, and easy-to-use port of 7zip command-line binaries (7za) for Python."

project_urls = {
    'Home page': f'https://pypi.org/project/{__name__}',
    'Source Code': f'https://github.com/{__author__}/{__name__}',
    'Documentation': f'https://{__name__}.cyopsys.com/docs',
}

# Search for version in the format: "- X.X.X"
with open('docs/CHANGELOG.md', 'r') as changelog_file:
    version_match = re.search(r'^-\s*(\d+\.\d+\.\d+)', changelog_file.read(), re.MULTILINE)

if version_match:
    __version__ = version_match.group(1)
    print(f"Latest version found in CHANGELOG.md: {__version__}")
else:
    __version__ = "0.0.0"
    print("Failed to retrieve the latest version from CHANGELOG.md")

with open("README.md", "r") as rm:
    long_description = rm.read()

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
    include_package_data=True,
    package_data={'': [
        'bin/7za', 
        'README.md', 
        'docs/CHANGELOG.md', 
        'docs/LICENSE.md', 
        'docs/PLANNING.md', 
        'docs/USAGE.md'
    ]},
)