import os
from setuptools import setup, find_packages
from codecs import open  # For consistent encoding

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

packages = find_packages(exclude=['tests'])

setup(
    name='NodeCalculator',
    version='2.0.1',
    description='This OpenSource Python module allows you to create node networks in Autodesk Maya by writing math formulas.',
    long_description=long_description,
    url='https://github.com/mischakolbe/node_calculator',
    license='Modified Apache 2.0 License',
    packages=packages,
    install_requires=requirements,
)