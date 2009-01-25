#!/usr/bin/env python
from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='django-microblogging',
    version=version,
    description='OpenMicroblogging support for Django',
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='omb,microblogging,django',
    author='Jay Graves',
    author_email='jay@skabber.com',
    url='http://github.com/skabber/django-omb/tree/master',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)


