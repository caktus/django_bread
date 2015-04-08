from setuptools import setup


setup(
    name='django_bread',
    version='0.0.3',
    packages=['bread'],
    url='https://github.com/caktus/django_bread',
    license='APL2',
    author='Dan Poirier',
    author_email='dpoirier@caktusgroup.com',
    description='Helper for building BREAD interfaces',
    install_requires=[
        'django-filter>=0.9.2,<1.0',
        'django-vanilla-views>=1.0.3,<2.0',
    ],
    # test_requires=[
    #     'django>=1.7.7',  # Should we require this explicitly?
    #     'factory_boy==2.3.1',
    # ],
    long_description=open('README.rst').read(),
    classifiers=[
        # FIXME: Add Django here
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
    ],
)
