#!/usr/bin/env python3

from setuptools import setup, find_packages
import sys

version='1.1.0'

with open('requirements.txt', 'r') as f:
  reqs = [line.strip() for line in f.readlines()]

setup(
    zip_safe=True,
    name='sosbot',
    version=version,
    long_description="Discord bot created for SOS 497",
    classifiers=[
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: GNU General Public License (GPL)",
      "Programming Language :: Python :: 3",
    ],
    keywords='discord, google googleapis',
    author='John Casey',
    author_email='jdcasey@commonjava.org',
    url='https://github.com/sos497/sosbot',
    license='APLv2',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=reqs,
    test_suite="tests",
    entry_points={
      'console_scripts': [
        'sosbot = sosbot:start',
      ],
    }
)

