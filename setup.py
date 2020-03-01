#!/usr/bin/env python3
from distutils.core import setup


setup(name='python-soundfilter',
      version='0.0.1',
      description='Python Distribution Utilities',
      author='Harry He',
      url='https://github.com/harryhecanada/python-soundfilter',
      install_requires=['sounddevice', 'pyqt5', 'numpy', 'matplotlib'],
      scripts=['soundfilter', 'spectrum_analyzer', 'gui']
    )