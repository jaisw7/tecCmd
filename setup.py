#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from setuptools import setup
import sys


# Python version
if sys.version_info[:2] < (3, 3):
    print('DGFS requires Python 3.3 or newer')
    sys.exit(-1)

# DGFS version
vfile = open('dgfs1D/_version.py').read()
vsrch = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", vfile, re.M)

if vsrch:
    version = vsrch.group(1)
else:
    print('Unable to find a version string in dgfs1D/_version.py')

# Modules
modules = [
    
]

# Data
package_data = {
    
}

# Hard dependencies
install_requires = [
    'numpy >= 1.8',
    'pytecplot >= 0.9'
]

# Soft dependencies
extras_require = {
    
}

# Scripts
console_scripts = [
    'tecCmd = tecCmd.tecCmd:__main__'
]

# Info
classifiers = [
    'License :: GNU GPL v2',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.3',
    'Topic :: Scientific/Engineering'
]

long_description = '''tecCmd is a utility for generating publication quality plots effortlessly'''

setup(name='tecCmd',
      version=version,
      description='Plot generation for scientific publishing',
      long_description=long_description,
      author='Purdue University, West Lafayette',
      author_email='jaisw7@gmail.com',
      url='http://www.github.com/jaisw7',
      license='GNU GPL v2',
      keywords='Applied Mathematics',
      packages=['dgfs1D'] + modules,
      package_data=package_data,
      entry_points={'console_scripts': console_scripts},
      install_requires=install_requires,
      extras_require=extras_require,
      classifiers=classifiers
)
