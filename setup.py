from setuptools import setup

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name="spotty",
    version="0.0.0",
    install_requires=requirements,
)