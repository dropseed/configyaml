#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'pyyaml',
]

test_requirements = [
    # TODO: put package test requirements here
    'pytest',
]

setup(
    name='config_loader',
    version='0.1.0',
    description="A config loading and parsing package",
    long_description=readme + '\n\n' + history,
    author="Dropseed",
    author_email='python@dropseed.io',
    url='https://github.com/dropseedlabs/config-loader',
    packages=[
        'config_loader',
    ],
    package_dir={'config_loader':
                 'config_loader'},
    entry_points={
        'console_scripts': [
            'config_loader=config_loader.cli:main'
        ]
    },
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
