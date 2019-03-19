#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup

setup(name='policyuniverse',
      version='1.3.0.1',
      description='AWS IAM Policy Utilities',
      author='Patrick Kelley',
      author_email='pkelley@netflix.com',
      url='https://github.com/Netflix-Skunkworks/policyuniverse',
      keywords = ['iam', 'policy', 'wildcard'],
      packages=['policyuniverse'],
      package_data={
          'policyuniverse': [
              'data.json'
          ]
      },
      include_package_data=True,
      zip_safe=False
     )
