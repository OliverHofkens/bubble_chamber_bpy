#!/usr/bin/env python

from setuptools import find_packages, setup

from bubble_chamber_bpy import __version__

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    author="Oliver Hofkens",
    author_email="oli.hofkens@gmail.com",
    name="bubble-chamber-bpy",
    version=__version__,
    description="Bubble chamber simulation in Blender + Python",
    long_description=readme,
    include_package_data=True,
    packages=find_packages(include=["bubble_chamber_bpy"]),
    setup_requires=[],
    install_requires=[],
    test_suite="tests",
    tests_require=["tox"],
    entry_points={
        "console_scripts": ["bubble-chamber-bpy=bubble_chamber_bpy.main:main"],
    },
)
