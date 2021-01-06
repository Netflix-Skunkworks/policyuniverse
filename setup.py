#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup
import os

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

tests_require = ["pytest", "coveralls"]
dev_require = ["pre-commit", "black"]

setup(
    name="policyuniverse",
    version="1.3.2.20210106",
    description="Parse and Process AWS IAM Policies, Statements, ARNs, and wildcards.",
    long_description=open(os.path.join(ROOT, "README.md")).read(),
    long_description_content_type="text/markdown",
    author="Patrick Kelley",
    author_email="patrickbarrettkelley@gmail.com",
    url="https://github.com/Netflix-Skunkworks/policyuniverse",
    keywords=[
        "iam",
        "arn",
        "action_groups",
        "condition",
        "policy",
        "statement",
        "wildcard",
    ],
    packages=["policyuniverse"],
    package_data={"policyuniverse": ["data.json"]},
    include_package_data=True,
    zip_safe=False,
    extras_require={"tests": tests_require, "dev": dev_require},
)
