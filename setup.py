#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import re

from setuptools import setup


required = [l for l in open('requirements/base.txt').read().split("\n")]
required_test = [l for l in open('requirements/test.txt').read().split("\n")]

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
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=["setuptools"] + required,
    license=refind('__license__'),
    entry_points={
        'console_scripts': ['exist=exist.cli:main'],
    },
    test_suite='nose.collector',
    tests_require=required_test,
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
)
