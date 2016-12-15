#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup

setup(name='iampoliciesgonewild',
      version='1.0.6.2',
      description='AWS IAM Policy Expander Minimizer',
      author='Patrick Kelley',
      author_email='pkelley@netflix.com',
      url='https://github.com/monkeysecurity/iampoliciesgonewild',
      keywords = ['iam', 'policy', 'wildcard'],
      packages=['iampoliciesgonewild'],
      package_data={
          'iampoliciesgonewild': [
              'master_permissions.json',
          ]
      },
      include_package_data=True,
      zip_safe=False
     )
