#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

install_requires = open("requirements.txt").read().split('\n')
readme_content = open("README.rst").read()

def gen_data_files(package_dir, subdir):
    import os.path
    results = []
    for root, dirs, files in os.walk(os.path.join(package_dir, subdir)):
        results.extend([os.path.join(root, f)[len(package_dir)+1:] for f in files])
    return results

ino_package_data = gen_data_files('ino', 'make') + gen_data_files('ino', 'templates')

setup(
    name='ino',
    version='0.3.3',
    description='Command line toolkit for working with Arduino hardware',
    long_description=readme_content,
    author='Victor Nakoryakov, Amperka Team',
    author_email='victor@amperka.ru',
    license='MIT',
    keywords="arduino build system",
    url='http://inotool.org',
    packages=['ino', 'ino.commands'],
    scripts=['bin/ino'],
    package_data={'ino': ino_package_data},
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Embedded Systems",
    ],
)
