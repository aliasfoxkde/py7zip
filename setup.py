import os
import re
from setuptools import setup

__name__ = 'py7za'

project_urls = {
    'Home page': 'https://pypi.org/project/py7za',
    'Source Code': 'https://gitlab.com/Jaap.vanderVelde/py7za',
    'Documentation': 'https://py7za.readthedocs.io/'
}

version_fn = os.path.join(__name__, "_version.py")
__version__ = "unknown"
try:
    version_line = open(version_fn, "rt").read()
except EnvironmentError:
    pass  # no version file
else:
    version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    m = re.search(version_regex, version_line, re.M)
    if m:
        __version__ = m.group(1)
    else:
        print(f'unable to find version in {version_fn}')
        raise RuntimeError(f'If {version_fn} exists, it is required to be well-formed')

with open("README.md", "r") as rm:
    long_description = rm.read()

setup(
    name="py7za",
    packages=['py7za'],
    version=__version__,
    license='MIT',
    author="BMT, Jaap van der Velde",
    author_email="jaap.vandervelde@bmtglobal.com",
    description="Description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/Jaap.vanderVelde/py7za',
    download_url='https://gitlab.com/Jaap.vanderVelde/py7za/repository/archive.zip?ref='+__version__,
    keywords=['package'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    extras_require={
        'box': ['conffu'],
        'dev': ['mkdocs']
    },
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'py7za-box=py7za.py7za_box:cli_entry_point',
            'box=py7za.py7za_box:cli_box_entry_point',
            'unbox=py7za.py7za_box:cli_unbox_entry_point',
        ],
    },
    include_package_data=True,
    package_data={'': ['bin/7za.exe', 'bin/7za-license.txt', 'bin/GNU_LGPL.txt']},
)
