# SETUP
This document outlines the steps needed to contribute to this project. A workflow is 
already established and several steps automated, and while these steps can still be 
done manually, for the purpose of consistancy and ease please use the outlined best 
practices found here.

## Prerequisites

### PyPi Setup
These steps only need to be taken if you have access to the root PyPi package library
and account.

- Steps
  - Login to PyPi and create an API key
  - Create an environment variable called PYPI_API_KEY
  - Copy the API key into the User Environment variable
  
## Publishing Changes
The "Push.bat" script is currently set to dynamically commit changes, include 
an auto-commit message if none is provided, build and publish updates made the 
PyPi packages automatically based on the PYPI_API_KEY, and cleanup. The build
and PyPi publishing will only occur on version change, which is dynamically
reflected by simply updating the CHANGELOG.md file. Standard non-version commits
will be ignored.

`push -m "{Message}"`

### Manual Publishing Steps
The following commands are dynamically ran by the "push.bat" file, in the case 
the repo version is higher, and the PYPI_API_KEY envernmnet variable is set, 
then publish changes to PyPi project. However, this is how it would be done
manually if needed.

```pycon
    # Builds Python Packages
    python setup.py sdist bdist_wheel
	
	# Uploads Python Packages to PyPi
	twine upload -u api -p %PYPI_API_KEY% dist/*
```

## Versioning
Versioning changes are based on {Major}.{Minor}.{Bug}.
