.. _installation:

Installation
============

Django Bread is on `PyPI <https://pypi.org/>`_. To install, add this to your requirements.txt::

    django-bread==0.6.0

Just change ``0.6.0`` in that example to the version that you
want to install.  Or leave it out to get the latest release.

Then run::

    pip -r requirements.txt

as usual.

Django
------

* Add 'bread' to your ``INSTALLED_APPS``
* In any template where you're using Bread views, load bread's javascript
  files, using something like::

      <script src="{% static 'js/URI.js' %}"></script>
      <script src="{% static 'js/bread.js' %}"></script>
