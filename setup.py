#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

# Package meta-data.
#Package based on capt by Craig Tomkow (https://github.com/ctomkow/capt')
NAME = 'capt'
DESCRIPTION = 'A nettool built on Cisco Prime\'s API'
URL = 'https://github.com/tmanfree/capt'
EMAIL = 'tmanfree@hotmail.com'
AUTHOR = 'Thomas Mandzie'
REQUIRES_PYTHON = '>=3.5.0'
VERSION = '0.2.1'

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      url=URL,
      author=AUTHOR,
      author_email=EMAIL,
      license='MIT',
      packages=["capt", "capt.connector", "capt.function", "capt.procedure", "capt.utils"],
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
