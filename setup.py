#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pytransact',
    version='1.0',
    description='pytransact aims to simplify payment processing with Bitcoin by abstracting away Bitcoin Core RPC calls',
    long_description=open('README.md').read(),
    author='Reuben S',
    author_email='',
    maintainer='Reuben S',
    maintainer_email='',
    url='https://github.com/reuben-s/pytransact',
    packages=['pytransact'],
    install_requires=[
        'aiohttp'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License', 'Operating System :: OS Independent'
    ]
)