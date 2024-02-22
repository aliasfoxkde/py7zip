# py7zip
An unofficial, cross platform, lightweight, and easy to use wrapper for 7zip command line binaries (7za) in Python. 
Unlike other libraries, this one fully supports 7zip natively, is easy to setup/install, and is "pythonic" with 
the intent to be used in code and scripts, not through the terminal. Additionally, you CAN use the '7za' binaries
directly as the specific binaries for your system will be installed automatically and you can therefor use '7za' 
direcly from the terminal/cli/cmd). This also lends to making cross platform apps using this module.

[repo-url]: https://github.com/aliasfoxkde/py7zip/blob/main/docs

## Why Choose py7zip?
- **Seamless Integration**: Unlike other libraries, py7zip seamlessly integrates 7zip functionality directly into Python, 
  eliminating the need for external dependencies or cumbersome command-line executions.
- **Cross-Platform Compatibility**: Whether you're running Windows, Linux, or Mac, py7zip ensures consistent performance 
  and reliability across all major operating systems.
- **Pythonic Design**: With a focus on adhering to Python's idiomatic principles, py7zip boasts an intuitive API that is 
  easy to understand and use within your codebase.
- **Lightweight and Efficient**: Despite its robust feature set, py7zip remains remarkably lightweight, occupying less 
  than 1MB of disk space.

## Usage
### Install using Pip/PyPi (Default; most common)
- `pip install py7zip`

### Install using Git Clone
- Browse to the location to install and open terminal/cmd
- `git clone https://github.com/aliasfoxkde/py7zip.git`
- `pip install .`

### Install Using Pip+Git (Alternative)
- `pip install git+https://github.com/aliasfoxkde/py7zip.git`

### Documentation
- [**FEATURES.md**](repo-url/FEATURES.md): reference documentation that details the features of this module as well as 7zip.
- [**USAGE.md**](repo-url/USAGE.md): includes detailed instructions on how to use this module.
- [**PLANNING.md**](repo-url/PLANNING.md): includes Tasks, Improvements, and General planning stages.
- [**CHANGELOG.md**](repo-url/CHANGELOG.md): includes versioning and a list of changes made between them.
- [**LICENSE.md**](repo-url/LICENSE.md): includes all licensing information for use of this module.
- **NOTE**: Documentation is broken down into parts and can be found in ./docs

## Platforms Supported and Tested:
- [ ] Linux x86-64 (64-bit)
- [ ] Linux x86 (32-bit)
- [ ] Linux arm64 (64-bit)
- [ ] Linux arm (32-bit)
- [ ] macOS (arm64 / x86-64)
- [ ] Windows x64 (64-bit)
- [ ] Windows x86 (32-bit )
- [ ] Windows arm64 (64-bit)