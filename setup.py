#!/usr/bin/env python

"""
distutils/setuptools install script.
"""
import os
import re
import sys

from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


requires = [
    'pysdl2 >= 0.9.3',
    'six >= 1.10'
]


def get_version():
    init = open(os.path.join(ROOT, 'sdl2ui', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='pysdl2-sdl2ui',
    version=get_version(),
    description='A Python library make simple UI using pysdl2',
    long_description=open('README.md').read(),
    author='Cecile Tonglet',
    url='https://github.com/cecton/pysdl2-sdl2ui',
    scripts=[],
    zip_safe=False,
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    package_data = {
        'sdl2ui': ['data/*.png'],
    },
    install_requires=requires,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    license="MIT",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
