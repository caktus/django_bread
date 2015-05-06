.. _templates:

Templates
=========

This document describes how to use templates with Django Bread.

Template Context
----------------

In addition to the context variables that Django Vanilla Views provides, Django Bread provides the
following to all of your templates::

        Variable             Description
        --------             -----------
        bread                Bread object
        verbose_name         Model's verbose_name field
        verbose_name_plural  Model's verbose_name_plural field
        base_template        The default base_template that should be extended.
        may_{action}         (i.e. may_browse, may_read, etc.) Boolean describing whether user has specified permission

Certain action views provide some additional variables. The Browse view has ``columns`` and
``filter``. The Read view has ``form``.

Override ``get_context_data`` to change the variables provided to your template:

.. code-block:: python

   class MyBrowseView(BrowseView):
       def get_context_data(self, **kwargs):
           data = super(BrowseView, self).get_context_data(**kwargs)
           data['my_special_var'] = 42
           return data


Template Resolution
-------------------

There are various ways to configure how and in what order Django Bread searches for the proper
template for your view.

By default, each Django Bread view will search first in an app-specific location (described below),
and then fall back to the templates provided by the Django Bread package.

App-specific location
^^^^^^^^^^^^^^^^^^^^^

The app-specific location is described by this pattern: ``{app_label}/{model}_{view}.html``.
For example, if your app's name is MyApp and your model's name is MyModel, Django Bread will look
for a browse template in ``myapp/mymodel_browse.html``.

Customization
^^^^^^^^^^^^^

There are 3 ways that you can customize this behavior even further:

1. Specify ``template_name_pattern`` in your Bread object. All views in that Bread object will then
   search in the app-specific location first (described above), then search
   ``template_name_pattern``, and then fall back to the Django Bread provided templates. The value
   supplied to ``template_name_pattern`` is a string that can take zero or more placeholders with
   the names ``app_label``, ``model``, or ``view``. An example of a valid pattern would be
   ``'{app_label}/special_{model}_{view}.html'``. Note that you can use this technique to implement
   site-wide customization by creating a subclass of Bread with ``template_name_pattern`` set, and
   then use that subclass (or children of it) throughout your site.

2. Set the ``template_name`` attribute in your View to the exact template that you want for that
   view. Example:

   .. code-block:: python

      class MyBrowseView(BrowseView):
          template_name = 'my/special-location.html'


3. Override ``get_template_names`` in a specific action View. This method should return a tuple of
   strings representing template locations to search. In most cases, using #3 is a simpler way to
   achieve this. But if you have a situation where you need a list of templates to be searched then
   here is an example on how to do that:

   .. code-block:: python

      class MyBrowseView(BrowseView):
          def get_template_names(self):
              return ('my/special-location.html', )

In addition to these template resolution rules, it's important to remember Django's own default
rules. If you have a template with the same name in 2 different applications, then whichever app is
listed first in INSTALLED_APPS wins. So, another way to get site-wide customization without using #2
above is to create templates named `bread/{activity}.html` in one of your local apps and make sure
it's listed before ``bread``.

Caveat
^^^^^^

We mentioned above that each View is matched to a template with the same name (BrowseView ->
'...browse.html'). This is true for everything except the AddView. Because add and edit templates
are so similar, the AddView connects to the 'edit.html' template. There is no 'add.html' template.
If you need your AddView to have its own template, there are 2 ways you can accomplish this. Either
use methods #3 or #4 above, or set ``template_name_suffix`` in your AddView class. It defaults to
``_edit``, but if you change it to ``_add`` then your AddView will be linked to a
``{app_label}/{model}_add.html`` template instead.
