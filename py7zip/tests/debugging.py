# Development Testing
import os
# import py7zip
from py7zip import py7zip


if __name__ == "__main__":
    py7z = py7zip.Py7zip()
    # print(py7z.get_binary_url())
    # print(py7z.setup())
    py7z.cd(os.path.dirname(py7zip.__file__))
    py7z.decompress("7z2301-src.7z", "7zTemp1")
    py7z.compress("*", "7zTemp1")
