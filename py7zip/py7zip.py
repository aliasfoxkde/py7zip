import subprocess
import platform
import os
import urllib.request
import sys
from general import get_version


class Py7zip:
    """ An unofficial, cross-platform, lightweight, and easy-to-use wrapper
        for 7zip command-line binaries (7za) in Python. """

    def __init__(self, verbose=False, debug=False):
        """ Initializes the class and variables. """
        self.__version__ = get_version()
        
        self.verbose = verbose
        self.debug = debug

        self.platform = platform.system().lower()
        self.supported = ['windows', 'linux', 'darwin']
        self.architecture = platform.architecture()[0]
        self.username = 'aliasfoxkde'
        self.app_name = 'py7zip'
        self.base_bin_url = f'https://github.com/{self.username}/{self.app_name}/raw/main/bin/'
        self.debug_info = platform.uname()

        # Move platform check to dedicated function
        if platform.machine() in ['AMD64', 'x86_64']:
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

    @staticmethod
    def cd(directory_path):
        os.chdir(directory_path)

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
        if self.platform not in self.supported:
            raise NotImplementedError(f"Platform '{self.platform}' is not supported.")
        return self.url

    def wrapper(self, src, dst, options='', method="decompress"):
        """ Method used to extract an archive. """
        if method == "compress":
            command = f'"7za{self.extension}" a "{dst}" "{src}" {options}'
            success_msg = f"Backup created from '{src}' to '{dst}'."
            error_msg = f"Failed to extract archive from '{src}' to '{dst}'."
        else:  # "compress" method as default
            command = f'"7za{self.extension}" x "{src}" -o"{dst}" {options}'
            success_msg = f"Extracted archive from '{src}' to '{dst}'"
            error_msg = f"Failed to create backup from '{src}' to '{dst}'."

        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
            if self.debug:
                print(result.stdout)
            if self.verbose:
                print(success_msg)
        except subprocess.CalledProcessError as e:
            if self.debug:
                print(f"Error: {e.stderr}.")
            if self.verbose:
                print(error_msg)

    def decompress(self, src, dst, options=''):
        """ Method used to extract an archive. """
        self.wrapper(src, dst, options='', method="decompress")

    def extract(self, src, dst, options=''):
        """ Alias used for 'compress' method. """
        self.wrapper(src, dst, options='', method="decompress")

    def compress(self, src, dst, options=''):
        """ Method used to backup files, folders, or directories to an archive. """
        self.wrapper(src, dst, options='', method="compress")

    def archive(self, src, dst, options=''):
        """ Alias used for decompress method. """
        self.wrapper(src, dst, options='', method="compress")

    def backup(self, src, dst, options=''):
        """ Alias used for decompress method. """
        self.wrapper(src, dst, options='', method="compress")

    def full(self, src, dst, options=''): pass
    def incremental(self, src, dst, options=''): pass
    def differential(self, src, dst, options=''): pass

    def snapshot(self, src, dst, options=''):
        """ Streamlines the process for creating a snapshot. """
        pass


if __name__ == "__main__":
    print("This module is intended to be imported, not run directly!")
