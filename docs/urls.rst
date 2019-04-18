.. _urls:

URLs
====

Calling `.get_urls()` on a Bread instance returns a urlpatterns
list intended to be included in a URLconf.

Example usages::

    urlpatterns += MyBread().get_urls()

or::

    urlpatterns = (
        ...,
        path('', include(MyBread().get_urls()),
        ...
    )

By default, the patterns returned will be of the form::

           Operation    Name                   URL
           ---------    --------------------   --------------------------
           Browse       browse_<plural_name>   <plural_name>/
           Read         read_<name>            <plural_name>/<pk>/
           Edit         edit_<name>            <plural_name>/<pk>/edit/
           Add          add_<name>             <plural_name>/add/
           Delete       delete_<name>          <plural_name>/<pk>/delete/

`name` is the lowercased name of the model.

`plural_name` is `name` with an `s` appended, but can be overridden by
setting `plural_name` on the Bread view.

If a restricted set of views is passed in the 'views' parameter, then
only URLs for those views will be included.

So, if your bread class looked like::


    class MyBread(Bread):
        model = BasicThingy
        plural_name = 'basicthingies'

Then your URLs returned by `.get_urls()` would look like::

       Operation    Name                   URL
       ---------    --------------------   --------------------------
       Browse       browse_basicthingies   basicthingies/
       Read         read_basicthingy       basicthingies/<pk>/
       Edit         edit_basicthingy       basicthingies/<pk>/edit/
       Add          add_basicthingy        basicthingies/add/
       Delete       delete_basicthingy     basicthingies/<pk>/delete/

If for some reason you didn't want your URLs to all start with ``<plural_name>/``,
then you can pass ``prefix=False`` to ``.get_urls()`` and you'll get back
"bare" URLS::

       Operation    Name                   URL
       ---------    --------------------   --------------------------
       Browse       browse_basicthingies
       Read         read_basicthingy       <pk>/
       Edit         edit_basicthingy       <pk>/edit/
       Add          add_basicthingy        add/
       Delete       delete_basicthingy     <pk>/delete/

Then you'd want to include them into your URLconf with some prefix of your own
choosing, e.g.::

    urlpatterns = (
        ....
        path('things/', include(MyBread().get_urls(prefix=False)),
        ...
    )
