#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'capt'
DESCRIPTION = 'A nettool built on Cisco Prime\'s API'
URL = 'https://github.com/ctomkow/capt'
EMAIL = 'ctomkow@gmail.com'
AUTHOR = 'Craig Abt Tomkow'
REQUIRES_PYTHON = '>=3.5.0'
VERSION = '0.1.12'

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      url=URL,
      author=AUTHOR,
      author_email=EMAIL,
      license='MIT',
      packages=["capt", "capt.connector", "capt.function", "capt.procedure"],
      install_requires=[
                  'urllib3>=1.13.1',
                  'requests>=2.9.1',
                  'argcomplete>=1.9.4',
            ],
      entry_points={
            'console_scripts': [
                'capt=capt.capt:Capt',
            ],
        },
      )
