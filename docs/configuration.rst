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

    path('', include(MyBreadView().get_urls())),

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

get_additional_context_data
    Override this method to add data to the template context for all views.
    You must include the data provided by Bread too, e.g.::

        def get_additional_context_data(self):
            context = super().get_additional_context_data()
            context['my_var'] = compute_my_value()
            return context

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
    'browse', 'view', 'edit', 'add', and 'delete'.  Then `_` and the
    lowercased model name are appended to get the complete permission name
    that a user must have to access the view. E.g. if your model is
    `MyModel` and you leave the default `perm_name` on the browse view,
    the user must have `browse_mymodel` permission.

    (Note that the permission for the "read" view is "view", not "read".
    It's a little confusing in this context, but "view" is what Django
    decided on for its standard read-only permission.)

template_name_suffix
    The default string that the template this view uses will end with.
    Defaults are '_browse', '_read', '_edit', '_edit' (not '_add'), and '_delete'.
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
    the default template, obviously). 'attrname' may also be a dunder method
    like `__unicode__` or `__len__`.

filterset
    filterset class to use to control filtering. Must be a subclass
    of django-filters' `django_filters.FilterSet` class.

paginate_by
    Limit browsing to this many items per page, and add controls
    to navigate among pages.

search_fields
    If set, enables search. Value is a list or tuple like the
    `same field <https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.search_fields>`_
    on the Django admin.

    This also enables display of a search input box in the default browse
    template.

    If there's a GET query parameter named ``q``, then its value will be split into
    words, and results will be limited to those that contain each of the words in
    at least one of the specified fields, not case sensitive.

    For example, if search_fields is set to ['first_name', 'last_name'] and a user
    searches for john lennon, Django will do the equivalent of this SQL WHERE clause::

        WHERE (first_name ILIKE '%john%' OR last_name ILIKE '%john%')
        AND (first_name ILIKE '%lennon%' OR last_name ILIKE '%lennon%')

    To customize the search behavior, you can override the ``get_search_results``
    method on the browse view, which has the same signature and behavior as
    the
    `same method <https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_search_results>`_
    in the admin.

search_terms
    If set, should be translated text listing the data fields that the search will
    apply to. For example, if your ``search_fields`` are ``['name', 'phone', 'manager__name']``,
    then you might set ``search_terms`` to ``_('name, phone number, or manager's name')``.
    Then ``search_terms`` will be available in the browse template context to help
    the user understand how their search will work.

sorting
    The default browse template will include sort controls on the column headers
    for columns that are sortable.

    It's a good idea to define a default ordering in the model's ``Meta`` class.
    After applying any sort columns specified by the user, Bread will add on any
    default orderings not already mentioned. That will result in the overall sort
    being stable, which is important if you want pagination to be sensible.
    (Otherwise, every time we show a new page, we could be working off a different
    sorting of the results!)  If nothing else, include a sort on the primary key.

    If you do not have control of the model and so cannot change its ordering there,
    you can add a ``default_ordering`` attribute to the browse view. Bread will use that
    if present, instead of the model's ordering.

    Configuring the browse view:

    If the second item in the ``columns`` entry for a column is not a valid specification
    for sorting on that column (e.g. it might refer to a method on the model), then
    you can add a third item to that column entry to provide a sort spec. E.g.
    ``('Office', 'name', 'name_english')``.

    Alternatively, if the second item in the ``columns`` entry for a column is valid for
    sorting, but you don't want the table to be sortable on that column, add a third
    item with a value of ``False``, e.g. ``('Date', 'creation_date', False)``.

    Query parameters:

    If there's a GET query parameter named ``o``, then its value will be split on
    commas, and each item should be a column number (0-based) optionally prefixed
    with '-'.  Any column whose number is included with '-' will be sorted
    descending, while any column whose number is included without '-' will be sorted
    ascending. The first column mentioned will be the primary sort column and so on.

    (Typically links are generated for you by Bread's Javascript, so you don't
    have to come up with these query parameters yourself.)

    Template context variables:

    If there's an ``o`` query parameter, there will be an ``o`` variable in the
    template context containing the value of it.  Otherwise, the ``o`` variable
    will exist but contain an empty string.

    There will be a context variable named ``valid_sorting_columns_json``
    which is a JSON string containing a list of the indexes of the columns that are
    valid to sort on.

    If you're not using the default bread templates or at least
    ``bread/includes/browse.html``, be sure to give your ``th`` elements a
    class of ``col_header`` and to include this javascript snippet::

        <script>
          var o_field = "{{o}}",
              valid_sorting_columns = JSON.parse("{{ valid_sorting_columns_json }}");
        </script>

    Styling:

    Any ``th`` element on a column that can be sorted will have the ``sortable``
    CSS class added to it, in case you want to style it differently.

    Additionally, a ``th`` element on a column that is sorted ascending will have
    the ``sort_asc`` class, or if sorted descending the ``sort_desc`` class, or
    if sortable but not current sorted, the ``unsorted`` class.

    Also, the ``th`` will have an attribute added, ``sort_column``, whose value
    will be ``1`` on the primary sort column, ``2`` on the secondary sort column,
    etc.

    This allows styling the columns with CSS like this::

        th.sortable.unsorted::after {
            content: "\00A0▲▼";
            opacity: 0.2;
        }
        table th.sortable.sortasc::after {
            content: "\00A0(" attr(sort_column)  "▲)";
        }
        table th.sortable.sortdesc::after {
            content: "\00A0(" attr(sort_column)  "▼)";
        }

    which will put " (1▲)" after the header on the primary sorting column if it's
    ascending, etc.


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
you would rather have more flexibility, subclass `bread.LabelValueReadView`
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
