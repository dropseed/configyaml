#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'pyyaml',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='config_loader',
    version='0.1.0',
    description="A config loading and parsing package",
    long_description=readme,
    author="Dropseed",
    author_email='python@dropseed.io',
    url='https://github.com/dropseedlabs/config-loader',
    packages=[
        'config_loader',
    ],
    package_dir={'config_loader':
                 'config_loader'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='config_loader',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
