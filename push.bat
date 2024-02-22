@echo off
REM Simple script for Auto-Committing Latest Repo Changes (could be scheduled)
REM This may be moved to Python, where flags can be also be used cross-platform.

REM Pipeline Improvements:
REM - Consider using AI to create commit message based on list of changes,
REM   and increment repository versioning, etc.

for /f %%A in ('git rev-parse --short HEAD') do set "commit_hash=%%A"

set "commit_message=Auto-commit changes #%commit_hash%"
set "custom_message="

REM Setup/Prepare Instructions (only done once)
REM Login to PyPi and create an API key
REM Create an environment variable called PYPI_API_KEY
REM pip install twine  # if it doesn't exist

REM Check current version of repository against Pip/PyPi
REM If repo version is higher, publish changes to PyPi project.
REM python setup.py sdist bdist_wheel  # build package
REM twine upload -u api -p %PYPI_API_KEY% dist/*

REM Cleanup build and distribution directories

REM Write metadata of repository details to JSON file

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
