#!/usr/bin/env python

import os

from setuptools import setup

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

tests_require = ["pytest", "coveralls", "bandit"]
dev_require = ["pre-commit", "black"]

setup(
    name="policyuniverse",
    version="1.5.1.20230817",
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
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
    classifiers=["License :: OSI Approved :: Apache Software License"],
    extras_require={"tests": tests_require, "dev": dev_require},
)
