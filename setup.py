import os
import re
from setuptools import setup

__name__ = 'py7zip'

project_urls = {
    'Home page': 'https://pypi.org/project/py7zip',
    'Source Code': 'https://github.com/aliasfoxkde/py7zip',
    'Documentation': 'https://py7zip.cyopsys.com/docs'
}

with open('docs/CHANGELOG.md', 'r') as changelog_file:
    changelog_content = changelog_file.read()

# Search for version in the format: "- X.X.X"
version_match = re.search(r'- (\d+\.\d+\.\d+)', changelog_content)

if version_match:
    print(f"Latest version found in CHANGELOG.md: {latest_version}")
    __version__ = version_match.group(1)
else:
    print("Failed to retrieve the latest version from CHANGELOG.md")
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
    name="py7zip",
    packages=['py7zip'],
    version=__version__,
    license='MIT',
    author="Aliasfoxkde",
    author_email="aliasfoxkde@gmail.com",
    description="Description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/aliasfoxkde/py7zip',
    download_url='https://github.com/aliasfoxkde/py7zip/repository/archive.zip?ref='+__version__,
    keywords=['package'],
    classifiers=[
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    extras_require={
    },
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'py7zip=py7za.py7za:extract',
        ],
    },
    include_package_data=True,
    package_data={'': [
        'bin/7za', 
        'README.md', 
        'docs/CHANGELOG.md', 
        'docs/LICENSE.md', 
        'docs/PLANNING.md', 
        'USAGE.md']},
)
