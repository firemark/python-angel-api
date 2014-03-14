#!/usr/bin/env python3.3
import os

from setuptools import setup, find_packages


requires = [
    'requests',
    'flask',
    'elasticsearch'
]

setup(name='Python Angel Api',
      version='0.1',
      author='Marek Piechula (firemark)',
      author_email='marpiechula@gmail.com',
      url='',
      install_requires=requires,
      packages=find_packages())
