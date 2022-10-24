from setuptools import find_packages, setup

setup(
    name='netbox-inventory',
    version='0.9.0',
    description='Inventory asset management in NetBox',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
