from setuptools import find_packages, setup

from bread import __version__

setup(
    name="django_bread",
    version=__version__,
    packages=find_packages(),
    url="https://github.com/caktus/django_bread",
    license="APL2",
    author="Dan Poirier",
    author_email="dpoirier@caktusgroup.com",
    description="Helper for building BREAD interfaces",
    include_package_data=True,
    install_requires=[
        "django-filter",
        "django-vanilla-views",
    ],
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.2",
    ],
    zip_safe=False,  # because we're including media that Django needs
)
