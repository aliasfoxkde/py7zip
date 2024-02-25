import subprocess
import platform
import os
import urllib.request
import sys


class Py7zip:
    """ An unofficial, cross-platform, lightweight, and easy-to-use wrapper
        for 7zip command-line binaries (7za) in Python. """

    def __init__(self):
        """ Initializes the class and variables. """
        self.platform = platform.system().lower()
        self.supported = ['windows', 'linux', 'darwin']
        self.architecture = platform.architecture()[0]
        self.username = 'aliasfoxkde'
        self.app_name = 'py7zip'
        self.base_bin_url = f'https://github.com/{self.username}/{self.app_name}/tree/main/bin'
        self.debug_info = platform.uname()

        if 'AMD64' in platform.machine():
            self.sys_type = 'pc'
        elif 'arm' in platform.machine():
            self.sys_type = 'arm'
        else:
            raise NotImplementedError("No machine type could be detected. Exiting.")

        self.arch_type = {'32bit': 'x86', '64bit': 'x64', 'arm64': 'x64', 'arm32': 'x86'}[self.architecture]
        self.sys_platform = {'windows': 'win', 'linux': 'lin', 'darwin': 'mac'}[self.platform]
        self.extension = {'windows': '.exe', 'linux': '', 'darwin': ''}[self.platform]
        self.url = f'{self.base_bin_url}/{self.sys_platform}/{self.sys_type}/{self.arch_type}/7za{self.extension}'
        self.binary_path = os.path.join(os.path.dirname(__file__), f'7za{self.extension}')
        self.setup()

    def setup(self):
        """ Checks the system for prerequisites and performs the required steps. """
        try:
            if not os.path.exists(self.binary_path):
                self.download_binary()
        except Exception as err:
            print(err)

    def download_binary(self):
        """ Dynamically downloads the binary required for the given platform. """
        binary_url = self.get_binary_url()
        binary_dir = os.path.dirname(self.binary_path)
        os.makedirs(binary_dir, exist_ok=True)

        with urllib.request.urlopen(binary_url) as response, open(self.binary_path, 'wb') as out_file:
            out_file.write(response.read())
            os.chmod(self.binary_path, 0o755)

    def get_binary_url(self):
        """ Dynamically gets the URL of the required system binary. """
        # Useful commands: platform: .system(), .release(), platform.version()
        if self.platform not in self.supported:
            raise NotImplementedError(f"Platform '{self.platform}' is not supported.")
        return self.url

    def snapshot(self, src, dst, options=''):
        """ Streamlines the process for creating a snapshot. """
        pass
        
    def extract(self, src, dst, options=''):
        """ Method used to extract an archive. """
        command = f'"{self.binary_path}" x "{src}" -o"{dst}" {options}'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        print(result.stdout)
        if result.returncode == 0:
            print(f"Extracted archive from {src} to {dst}")
        else:
            print(f"Failed to extract archive from {src} to {dst}. Error: {result.stderr}")

    def backup(self, src, dst, options=''):
        """ Method used to backup files, folders, or directories to an archive. """
        def full(self, src, dst, options=''): pass
        def incremental(self, src, dst, options=''): pass
        def differential(self, src, dst, options=''): pass
        
        command = f'"{self.binary_path}" a "{dst}" "{src}" {options}'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        print(result.stdout)
        if result.returncode == 0:
            print(f"Backup created from {src} to {dst}")
        else:
            print(f"Failed to create backup from {src} to {dst}. Error: {result.stderr}")


if __name__ == "__main__":
    # Development Testing
    py7z = Py7zip()
    print(py7z.get_binary_url())
    print("This module is intended to be imported, not run directly!")
