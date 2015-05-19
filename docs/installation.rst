.. _installation:

Installation
============

Django Bread is not yet in PyPI (TODO), but it's pretty
easy to install the version you want using pip from github.
Add something like this to your requirements.txt::

    git+git://github.com/caktus/django_bread@0.0.6#egg=django_bread

Just change ``0.0.6`` in that example to the version that you
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

