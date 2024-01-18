import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="openimis-be-report",
    version='1.5.2',
    packages=find_packages(),
    include_package_data=True,
    license="GNU AGPL v3",
    description="The openIMIS Report reference module.",
    # long_description=README,
    url="https://openimis.org/",
    author="Xavier Gillmann",
    author_email="xgillmann@bluesquarehub.com",
    install_requires=[
        "django",
        "django-db-signals",
        "djangorestframework",
        "cached-property",
        "nepalicalendar",
        "openimis-be-core",
        "reportbro-lib",
        "reportbro-fpdf",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
