# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ship_it',
    version='0.1.1',
    install_requires=['fabric', 'PyYaml', 'six', 'virtualenv'],
    packages=find_packages(),
    url='github.com/robdennis/ship_it',
    license='MIT',
    author='Rob Dennis',
    author_email='rdennis+ship_it@gmail.com',
    description='thin build wrapper around fpm that enforces some best '
                'practices for created deb/rpms of python applications'
)