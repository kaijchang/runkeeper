from setuptools import setup
import os

setup(
    name='runkeeper',
    packages=['runkeeper'],
    version='0.1.2',
    description='Unofficial Python API Client for Runkeeper',
    author='Kai Chang',
    url='https://github.com/kajchang/runkeeper',
    license='MIT',
    long_description_content_type='text/markdown',
    long_description=open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'README.md')).read(),
    install_requires=[open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'requirements.txt')).read().split('\n')[:-1]]
)
