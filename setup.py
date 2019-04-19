from setuptools import setup, find_packages
from bread import VERSION

setup(
    name='django_bread',
    version=VERSION,
    packages=find_packages(),
    url='https://github.com/caktus/django_bread',
    license='APL2',
    author='Dan Poirier',
    author_email='dpoirier@caktusgroup.com',
    description='Helper for building BREAD interfaces',
    include_package_data=True,
    install_requires=[
        'django-filter>2,<2.2.0',
        'django-vanilla-views>=1.0.3,<2.0',
    ],
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
    ],
    zip_safe=False,  # because we're including media that Django needs
)
