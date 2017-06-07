#!/usr/bin/env python

from setuptools import setup
from time import strftime, gmtime

setup(
    name='bob_test',
    version='0.{}'.format(strftime("%s", gmtime())),
    description='BoB API Test Scripts',
    author='Kirei AB',
    author_email='info@kirei.se',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3 :: Only'
    ],
    url='https://github.com/kirei/bobtest/',
    packages=['bobtest_test'],
    install_requires=[
        'green',
        'pyjwkest',
        'requests',
        'ruamel.yaml',
        'setuptools'
    ],
)
