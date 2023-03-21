"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

from workflowhub import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Load requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='scipion-em-workflowhub',
    version=__version__,
    description='A Scipion plugin to make depositions to WorkflowHub',
    long_description=long_description,
    url='https://github.com/scipion-em/scipion-em-workflowhub',
    author='I2PC',
    author_email='scipion@cnb.csic.es',
    keywords='scipion workflowhub scipion-3.0',
    packages=find_packages(),
    install_requires=requirements,
    package_data={
       'workflowhub': ['WorkflowHub_logo.png', 'protocols.conf'],
    },
    entry_points={
        'pyworkflow.plugin': 'workflowhub = workflowhub'
    }
)