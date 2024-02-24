@echo off
REM Simple script for Auto-Committing Latest Repo Changes (could be scheduled)
REM This may be moved to Python, where flags can be also be used cross-platform.

REM Pipeline Improvements:
REM - Consider using AI to create commit message based on list of changes,
REM   and increment repository versioning, etc.

for /f %%A in ('git rev-parse --short HEAD') do set "commit_hash=%%A"

set "app_name=py7zip"
set "commit_message=Auto-commit changes #%commit_hash%"
set "custom_message="

REM Check current version of repository against Pip/PyPi
REM If repo version is higher, and API Key Set, publish changes to PyPi project.

REM Extract version from CHANGELOG.md
for /f "tokens=2 delims=- " %%v in ('type docs\CHANGELOG.md ^| findstr /b /c:"- "') do (
    set "changelog_version=%%v"
    REM goto compare_versions
)

REM :compare_versions
REM Check if PYPI_API_KEY is set
if not "%PYPI_API_KEY%" == "" (
    for /f "tokens=2 delims==" %%p in ('pip show py7zip ^| findstr /c:"Version"') do (
        set "pypi_version=%%p"
    )
	pause

    REM Compare versions
    if "%changelog_version%" GTR "%pypi_version%" (
        echo Repository version (%changelog_version%) is higher than PyPi version (%pypi_version%). Publishing to PyPi...
        python setup.py sdist bdist_wheel  REM Build package
        twine upload -u api -p %PYPI_API_KEY% dist/*
    ) else (
        echo Repository version (%changelog_version%) is not higher than PyPi version (%pypi_version%). Skipping PyPi publishing.
    )
) else (
    echo PYPI_API_KEY environment variable is not set. Skipping PyPi publishing.
)
pause

REM Cleanup build and distribution directories
echo Cleaning up build and distribution directories...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist py7zip.egg-info rmdir /s /q py7zip.egg-info

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
