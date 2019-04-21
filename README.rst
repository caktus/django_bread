Django Bread
============

Django Bread is a Django app to help build BREAD (Browse, Read, Edit,
Add, Delete) views for Django models.

It helps with default templates, url generation, permissions, filters,
pagination, and more.

This is relatively stable. We're using it in production and have attempted
to document the important parts, but feedback is welcome.

Supported versions
------------------

Django: 2.0, 2.1, 2.2
Python: 3.5, 3.6, 3.7

For Python 2.7 and/or Django 1.11 support, the 0.5 release series is identical (features-wise)
to 0.6 and is available on PyPI: https://pypi.org/project/django-bread/#history

Testing
-------

To run the tests, install "tox" ("pip install tox") and just run it:

    $ tox
    ...
