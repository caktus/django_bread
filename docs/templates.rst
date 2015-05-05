.. _templates:

Templates
=========

This document describes how to use templates with Django Bread.

Template Context
----------------

In addition to what Django Vanilla Views provides, Django Bread provides the following to all of
your templates::

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

The app-specific location is described by this pattern: ``{app_name}/{model_name}{activity}.html``.
For example, if your app's name is MyApp and your model's name is MyModel, Django Bread will look
for a browse template in ``myapp/mymodelbrowse.html``.

Customization
^^^^^^^^^^^^^

There are 3 ways that you can customize this behavior even further:

1. Specify ``template_name_pattern`` in your Bread object. All views in that Bread object will then
   search in the app-specific location first (described above), then search
   ``template_name_pattern``, and then fall back to the Django Bread provided templates. The value
   supplied to ``template_name_pattern`` is a string that can take zero or more placeholders with
   the names ``app_label``, ``model``, or ``view``. An example of a valid pattern would be
   ``'{app_label}/special_{model}_{view}.html'``.

2. Specify a Django setting ``BREAD['DEFAULT_TEMPLATE_NAME_PATTERN'] = 'blah'``. This will function
   like #1 above, except for ALL bread objects on your site. You can still override this
   customization with #1 for a specific bread object. Use this option to provide a site-wide
   default. If, for some reason, you omit one of the action templates, then we'll fall back to the
   Django Bread default.

3. Override ``get_template_names`` in a specific action View. This method should return a tuple of
   strings representing template locations to search. This is the most specific customization, and
   applies only to the Model/action view you override. Example:

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
Of course, this can be customized as described above, if you need different templates for your
AddView classes.
