#!/usr/bin/env python

from setuptools import setup, find_packages

try:
    README = open('README.rst').read()
except:
    README = None

try:
    REQUIREMENTS = open('requirements.txt').read()
except:
    REQUIREMENTS = None

setup(
    name='newspeak',
    version="0.1",
    description='Standalone Django based feed aggregator.',
    long_description=README,
    install_requires=REQUIREMENTS,
    author='Mathijs de Bruin',
    author_email='mathijs@visualspace.nl',
    url='http://github.com/bitsoffreedom/newspeak/',
    packages=find_packages(),
    include_package_data=True,
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
    entry_points={
        'console_scripts': [
            'newspeak = newspeak.runner:main',
        ],
    },
)
