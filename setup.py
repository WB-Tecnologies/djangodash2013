# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

version = __import__('clients_support').get_version()


def rel(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-clients-support',
    version=version,
    description='Client support application for django based projects', license='BSD',
    long_description=rel('README.md'),
    keywords='django clients support',
    author='WB-Technologies',
    author_email='ask@wbtech.ru',
    url='https://github.com/WB-Tecnologies/djangodash2013.git',
    platforms=['any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=["testproject","testproject.*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django >= 1.4',
        'South >= 0.8.2',
        'djangorestframework >= 2.3.8',
        'django-autocomplete-light >= 1.4.3',
    ]
)
