#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import re

from setuptools import setup


required = [l for l in open('requirements/base.txt').read().split("\n")]

mfinit = open('exist/__init__.py').read()
refind = lambda varname: re.search("%s = '([^']+)'" % varname, mfinit).group(1)

setup(
    name='exist',
    version=refind('__version__'),
    description='Exist API client implementation',
    long_description=open('README.md').read(),
    author=refind('__author__'),
    author_email=refind('__author_email__'),
    url='https://github.com/mattimck/python-exist',
    packages=['exist'],
    package_data={'': ['LICENSE'], '': ['requirements/*']},
    include_package_data=True,
    install_requires=["setuptools"] + required,
    license=refind('__license__'),
    entry_points={
        'console_scripts': ['exist=exist.cli:main'],
    },
    classifiers = [],
)
