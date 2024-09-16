import os
import re

def get_version(verbose=False):
    # Search for version in the format: "- X.X.X"
    changelog_path = os.path.join('..', 'docs', 'CHANGELOG.md')
    with open(changelog_path, 'r') as changelog_file:
        version_match = re.search(r'^-\s*(\d+\.\d+\.\d+)', changelog_file.read(), re.MULTILINE)

    if version_match:
        version = version_match.group(1)
        if verbose:
            print(f"Latest version found in CHANGELOG.md: {version}")
    else:
        version = "0.0.0"
        if verbose:
            print("Failed to retrieve the latest version from CHANGELOG.md")
    return version
    

def get_metadata():
    pass
            
        
if __name__ == "__main__":
    print("This module is intended to be imported, not run directly!")