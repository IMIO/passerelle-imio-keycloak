#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from setuptools import find_packages
from setuptools import setup

setup(
    name="passerelle-imio-ia-delib",
    version="1.0.0",
    author="iMio",
    author_email="support-ts@imio.be",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],
    url="https://dev.entrouvert.org/projects/imio/",
    install_requires=[
        "django>=2.2",
    ],
    zip_safe=False,
)
