# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='ship_it',
    version='0.1.0',
    requires=['fabric', 'PyYaml', 'six', 'virtualenv'],
    packages=['ship_it'],
    url='github.com/robdennis/ship_it',
    license='MIT',
    author='Rob Dennis',
    author_email='rdennis+ship_it@gmail.com',
    description='thin build wrapper around fpm that enforces some best '
                'practices for created deb/rpms of python applications'
)
