import subprocess
import platform
import os
import urllib.request
import sys


class Py7zip:
    """ An unofficial, cross-platform, lightweight, and easy-to-use wrapper
        for 7zip command-line binaries (7za) for Python. """

    def __init__(self):
        self.platform = platform.system().lower()
        self.architecture = platform.architecture()[0]
        self.binary_path = os.path.join(os.path.dirname(__file__), 'bin', '7za')

        if not os.path.exists(self.binary_path):
            self.download_binary()

    def download_binary(self):
        binary_url = self.get_binary_url()
        binary_dir = os.path.dirname(self.binary_path)
        os.makedirs(binary_dir, exist_ok=True)

        with urllib.request.urlopen(binary_url) as response, open(self.binary_path, 'wb') as out_file:
            out_file.write(response.read())
            os.chmod(self.binary_path, 0o755)

    def get_binary_url(self):
        architectures = {'32bit': 'x86', '64bit': 'x64', 'arm64': 'arm64', 'arm32': 'arm'}
        platform_urls = {
            'linux': f'https://example.com/7za_linux_{architectures[self.architecture]}',
            'darwin': f'https://example.com/7za_mac_{architectures[self.architecture]}',
            'windows': f'https://example.com/7za_windows_{architectures[self.architecture]}.exe'
        }

        if self.platform not in platform_urls:
            raise NotImplementedError(f"Platform '{self.platform}' is not supported.")

        return platform_urls[self.platform]

    def extract(self, src, dst, options=''):
        command = f'"{self.binary_path}" x "{src}" -o"{dst}" {options}'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        print(result.stdout)
        if result.returncode == 0:
            print(f"Extracted archive from {src} to {dst}")
        else:
            print(f"Failed to extract archive from {src} to {dst}. Error: {result.stderr}")

    def backup(self, src, dst, options=''):
        command = f'"{self.binary_path}" a "{dst}" "{src}" {options}'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        print(result.stdout)
        if result.returncode == 0:
            print(f"Backup created from {src} to {dst}")
        else:
            print(f"Failed to create backup from {src} to {dst}. Error: {result.stderr}")


if __name__ == "__main__":
    print("This module is intended to be imported, not run directly!")
