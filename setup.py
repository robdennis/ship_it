# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ship_it',
    version='0.6.0',
    install_requires=['invoke', 'PyYaml', 'six', 'virtualenv', 'click'],
    packages=['ship_it'],
    url='https://github.com/robdennis/ship_it',
    license='MIT',
    author='Rob Dennis',
    author_email='rdennis+ship_it@gmail.com',
    description='thin build wrapper around fpm that enforces some best '
                'practices for created deb/rpms of python applications',
    entry_points={
        'console_scripts': ['ship_it=ship_it.scripts:main']
        }
)
