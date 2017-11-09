.. _changes:

Change Log
==========

0.4.0 - Oct 31, 2017
--------------------

* Add support for Python 3.6
* Add support for Django 1.11
* Drop support for Django 1.9 (no longer supported by Django)
* Drop support for Python 3.4

Supported versions in this release are:

Django: 1.8, 1.10, 1.11
Python: 2.7, 3.5, 3.6


0.3.0 - Oct 19, 2016
--------------------

* Add CI coverage for Python 3.5
* Add support for Django 1.9 and 1.10

0.2.4 - Aug 21, 2015
--------------------

* Add migration to drop BreadTest table (#64)

0.2.3 - Jun 11, 2015
--------------------

* New release because 0.2.2 didn't have the right
  version number internally.

0.2.2 - Jun 9, 2015
-------------------

* Allow not sorting on columns (#60)

0.2.1 - Jun 6, 2015
-------------------

* Handle exception from related object does not exist (#58)

0.2.0 - Jun 3, 2015
-------------------

* Add Bread.get_additional_context_data(). (#57)

0.1.9 - Jun 2, 2015
-------------------

* Fix setting form_class on individual views (#55)

0.1.8 - May 21, 2015
--------------------

* Fix template so files can be uploaded from forms
* Fix javascript to not fail if `o_field` is not defined.

0.1.7 - May 21, 2015
--------------------

* Tweaks to sorting (includes breaking changes to how sorted columns
  are formatted; see docs).
* Fix searches with non-ASCII characters.

0.1.6 - May 19, 2015
--------------------

* Sortable columns in browse view

0.1.5 - May 14, 2015
--------------------

* Fix displaying search parameter in search field with results
* Fix filters disappearing if there are no results

0.1.4 - May 7, 2015
-------------------

* Add search
* Add doc for LabelValueReadView
* More flexible template resolution

0.1.3 - May 6, 2015
-------------------

* Add LabelValueReadView

0.1.2 - May 6, 2015
-------------------

* Use six for python 2/3 compatibility
* expose model verbose names to templates

0.1.1 - April 30, 2015
----------------------

* Allow omitting model names from URL patterns

0.1.0
-----

* Breaking changes to how Bread views are configured.
