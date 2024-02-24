@echo off
@title=AutoCommit Changes to Git
REM Simple script for Auto-Committing Latest Repo Changes (could be scheduled)

REM Pipeline Improvements:
REM - Consider using AI to create commit message based on list of changes,
REM   and increment repository versioning, etc.
REM - Move logic to Python, where flags can be also be used cross-platform.

for /f %%A in ('git rev-parse --short HEAD') do set "commit_hash=%%A"

set "app_name=py7zip"
set "commit_message=Auto-commit changes #%commit_hash%"
set "custom_message="
set "changelog_version="
set "pypi_version="
set "pip_version="

REM Check current version of repository against Pip/PyPi
REM If repo version is higher, and API Key Set, publish changes to PyPi project.

if not "%PYPI_API_KEY%" == "" (
	goto skip_version_check
)

REM Extract version from CHANGELOG.md
for /f "delims=- " %%v in ('type docs\CHANGELOG.md ^| findstr /b /c:"- "') do (
	set "changelog_version=%%v"
	
	REM Breaks out of loop on first match
	goto :break
)
:break

REM Retrieve version from PyPi
for /f %%v in ('curl -s https://pypi.org/pypi/%app_name%/json ^| jq -r ".info.version"') do (
	set "pypi_version=%%v"
)

REM Checks current module version
for /f "tokens=2 delims=: " %%v in ('pip show %app_name% ^| findstr /c:"Version"') do (
	set "pip_version=%%v"
)

REM Checks local pip version to PyPi version and if older, updates it (optional)
if "%pypi_version%" GTR "%pip_version%" (
	pip install -U %app_name%
	pip install -U twine
)

REM Checks PyPi version to Repo/CHANGELOG version
if %pypi_version% == %changelog_version% (
	echo PyPi and Repo version ^(%pypi_version%^) are the same. Skipping PyPi publishing.
) else (
	if %pypi_version% GTR %changelog_version% (
		echo PyPi Version is Newer! There must be an issue with the repo or CHANGELOG, please check.
	) else (
		echo Repository version ^(%changelog_version%^) is higher than PyPi version ^(%pypi_version%^). 
		echo Publishing Package to PyPi...
		python setup.py sdist bdist_wheel
		twine upload -u api -p %PYPI_API_KEY% dist/*
	)
)

REM Cleanup build and distribution directories
echo Cleaning up build and distribution directories...
if exist build\ (
	rmdir /s /q build
	rmdir /s /q dist
	rmdir /s /q *.egg-info
)
:skip_version_check

REM Loop through command line arguments
:parse_args
if "%~1" == "" goto run_git_commands
if "%~1" == "-m" (
    set "custom_message=%~2"
    shift
    shift
    goto parse_args
)
shift
goto parse_args

:run_git_commands
if not "%custom_message%" == "" (
    set "commit_message=%custom_message%"
)

git add .
git commit -m "%commit_message%"
git push

echo.
echo Auto-Commit Hash: %commit_hash%
echo Changes have been committed, script will exit in 5 seconds...
TIMEOUT 5