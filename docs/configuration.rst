.. _configuration:

Configuration
=============

Bread views are configured similar to some other class-based views, by
subclassing and setting attributes on the subclasses, then instantiating
one and adding it to your URL config.

The main class to subclass is ``Bread``::

    class MyBreadView(Bread):
        attrib1 = something
        attrib2 = somethingelse

then you can add it to a URL config something like this::

    url(r'^', include(MyBreadView().get_urls())),

See also :ref:`urls`.

Bread configuration
-------------------

There are a lot of things that can be configured, so they're somewhat
organized by which views they affect.  Any parameter that affects
multiple views (e.g. browse, read, edit) is set on what we'll call
the ``main`` class, that is, the class that is a subclass of ``Bread``.

Here are some of those common parameters.

model (required)
    The model class

exclude
    A list of names of fields to always exclude from any form classes that
    Bread generates itself. (Not used for any views that have a custom form
    class provided.)

form_class
    A model form class that Bread should use instead of generating one
    itself. Can also be overridden on individual views that use forms.

name
    A string to use in url names, permissions, etc. Defaults to the model's
    name, lowercased. Example: If the model class is ``MyModel``, the default
    name would be ``mymodel``.  See also :ref:`urls` and :ref:`templates`.

plural_name
    A string to use as the plural name where needed (see ``name``, :ref:`urls`,
    and :ref:`templates`).
    Default: the name with an ``s`` appended.

namespace
    A string with the URL namespace to include in the generated URLS.
    Default is `''`.  See also :ref:`urls`.

views
    A string containing the first letters of the views to include.
    Default is 'BREAD'.  Any omitted views will not have URLs defined and so will
    not be accessible.

Example::

    class MyBreadView(Bread):
        model = MyModel
        form_class = MyModelForm
        views = 'BRD'

Configuring individual views
----------------------------

To set things that only affect one view, subclass the default base
class for that view and set attributes on it, then configure the
main bread subclass to use your view subclass by setting these
attributes:

browse_view
    Use this class for the browse view. Default: `bread.BrowseView`

read_view
    Use this class for the read view. Default: `bread.ReadView`

edit_view
    Use this class for the edit view. Default: `bread.EditView`

add_view
    Use this class for the add view. Default: `bread.AddView`

delete_view
    Use this class for the delete view. Default: `bread.DeleteView`

Example::

    class MyBrowseView(bread.BrowseView):
        param1 = value1
        param2 = value2

    class MyBreadView(Bread):
        attrib1 = something
        attrib2 = somethingelse
        browse_view = MyBrowseView

Common view configuration parameters
------------------------------------

These can be set on any individual view class.

perm_name
    The base permission name needed to access the view. Defaults are
    'browse', 'read', 'edit', 'add', and 'delete'.  Then `_` and the
    lowercased model name are appended to get the complete permission name
    that a user must have to access the view. E.g. if your model is
    `MyModel` and you leave the default `perm_name` on the browse view,
    the user must have `browse_mymodel` permission.

template_name_suffix
    The default string that the template this view uses will end with.
    Defaults are 'browse', 'read', 'edit', 'edit' (not 'add'), and 'delete'.
    See also :ref:`templates`.


Browse view configuration
-------------------------

Subclass `bread.BrowseView` and set these parameters.

BrowseView is itself a subclass of Vanilla's ListView.

columns
    Iterable of ('Title', 'attrname') pairs to customize the columns
    in the browse view. 'attrname' may include '__' to drill down into fields,
    e.g. 'user__name' to get the user's name, or 'type__get_number_display' to
    call get_number_display() on the object from the type field.  (Assumes
    the default template, obviously).

filterset
    filterset class to use to control filtering. Must be a subclass
    of django-filters' `django_filters.FilterSet` class.

paginate_by
    Limit browsing to this many items per page, and add controls
    to navigate among pages.

Read view configuration
-----------------------

Subclass `bread.ReadView` and set these parameters.

ReadView itself is a subclass of Vanilla's DetailView.

exclude
    A list of names of fields to always exclude from any form classes that
    Bread generates itself. Not used in this view if a custom form class
    is provided.  If specified, replaces `exclude` from the `BreadView`
    subclass.

form_class
    specify a custom form class to use for this model in this view

Alternate read view configuration
---------------------------------

The default read view uses a form to describe which fields to display. If
you would rather have more flexibilty, subclass `bread.LabelValueReadView`
and set these parameters.

LabelValueReadView is a subclass of ReadView.

fields
    A list of 2-tuples of (label, evaluator) where the evaluator is reference
    to an object attribute, an object method, a function, or one of a few other
    options. In addition, the label can be automatically generated for you in
    some cases.

    See the class docstring for full details.

Edit view configuration
-----------------------

Subclass `bread.EditView` and set these parameters.

EditView itself is a subclass of Vanilla's UpdateView.

exclude
    A list of names of fields to always exclude from any form classes that
    Bread generates itself. Not used in this view if a custom form class
    is provided.  If specified, replaces `exclude` from the `BreadView`
    subclass.

form_class
    specify a custom form class to use for this model in this view


Add view configuration
----------------------

Subclass `bread.AddView` and set these parameters.

AddView itself is a subclass of Vanilla's CreateView.

exclude
    A list of names of fields to always exclude from any form classes that
    Bread generates itself. Not used in this view if a custom form class
    is provided.  If specified, replaces `exclude` from the `BreadView`
    subclass.

form_class
    specify a custom form class to use for this model in this view

