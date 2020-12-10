Django Bread
============

Django Bread is a Django app to help build BREAD (Browse, Read, Edit,
Add, Delete) views for Django models.

It helps with default templates, url generation, permissions, filters,
pagination, and more.

This is relatively stable. We're using it in production and have attempted
to document the important parts, but feedback is welcome.

Breaking change in 1.0.0
------------------------

Version 1.0.0 includes a breaking change! If you're using the default
view permissions, before upgrading, make sure you've
migrated your users and groups that have "read_{model_name}"
permissions to also have "view_{model_name}".  From 1.0.0 on, that's the
default permission a user needs to use the read views, because it's become the
standard Django permission for read-only access since Django 2.1.

If you're still on Django 2.0, don't upgrade django-bread until you
can get to at least Django 2.1. (Hopefully that's not the case, since
Django 2.0 has been out of support since April 1, 2019.)


Supported versions
------------------

Django: 2.2, 3.0, 3.1
Python: 3.7, 3.8, 3.9

For Python 2.7 and/or Django 1.11 support, the 0.5 release series is identical (features-wise)
to 0.6 and is available on PyPI: https://pypi.org/project/django-bread/#history


Maintainer Information
----------------------

We use Github Actions to lint (using pre-commit, black, isort, and flake8),
test (using tox and tox-gh-actions), calculate coverage (using coverage), and build
documentation (using sphinx).

We have a local script to do these actions locally, named ``maintain.sh``::

  $ ./maintain.sh

A Github Action workflow also builds and pushes a new package to PyPI whenever a new
Release is created in Github. This uses a project-specific PyPI token, as described in
the `PyPI documentation here <https://pypi.org/help/#apitoken>`_. That token has been
saved in the ``PYPI_PASSWORD`` settings for this repo, but has not been saved anywhere
else so if it is needed for any reason, the current one should be deleted and a new one
generated.

As always, be sure to bump the version in ``bread/__init__.py`` before creating a
Release, so that the proper version gets pushed to PyPI.


Questions or Issues?
--------------------

If you have questions, issues or requests for improvements please let us know on
`Github <https://github.com/caktus/django_bread/issues>`_.

Development sponsored by `Caktus Consulting Group, LLC
<https://www.caktusgroup.com/services>`_.
