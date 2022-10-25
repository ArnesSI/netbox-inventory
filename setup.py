import codecs
import os.path

from setuptools import find_packages, setup

with open('README.md', 'r', encoding='UTF-8') as fh:
    long_description = fh.read()


def read(rel_path):
    '''Read file from relative path to add to pypi long_description'''
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as file_path:
        return file_path.read()

setup(
    name='netbox-inventory',
    version='1.0.0',
    description='Inventory asset management in NetBox',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
