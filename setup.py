#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from telemetry import __VERSION__ as version


def get_requirements(filename):
    with open(filename) as f:
        requirements_list = []
        rows = f.readlines()
        for row in rows:
            row = row.strip()
            if (row.startswith('#') or row.startswith('git+ssh://') or
                    row.startswith('-r') or not row):
                continue
            else:
                requirements_list.append(row)
    return requirements_list


setup(
    name='telemetry',
    version=version,
    description=('''
        Telemetry is a python library to instrument your code and send
        metrics to a monitoring station.
    '''),
    url='https://github.com/daniloqueiroz/telemetry',
    author='Danilo Queiroz',
    author_email='dpenna.queiroz@gmail.com',
    license="GPLv3",
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='telemetry metrics influx',
    packages=find_packages(exclude=['tests']),
    test_suite='nose.collector',
    tests_require=get_requirements('dev_requirements.txt'),
    include_package_data=True,
)
