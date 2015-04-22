try:
    # Python 2
    from httplib import BAD_REQUEST
    from urllib import urlencode
except ImportError:
    # Python 3
    from http.client import BAD_REQUEST
    from urllib.parse import urlencode

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import Permission
from django.contrib.auth.views import redirect_to_login
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.forms.models import modelform_factory
from vanilla import ListView, DetailView, CreateView, UpdateView, DeleteView


"""
About settings.

You can provide a Django setting named BREAD as a dictionary.
Here are the settings, all currently optional:

DEFAULT_BASE_TEMPLATE: Default value for Bread's base_template argument

DEFAULT_TEMPLATE_NAME_PATTERN: Default value for Bread's
template_name_pattern argument.
"""


# Helper to get settings from BREAD dictionary, or default
def setting(name, default=None):
    BREAD = getattr(settings, 'BREAD', {})
    return BREAD.get(name, default)


class BreadViewMixin(object):
    """We mix this into all the views for some common features"""
    bread = None  # The Bread object using this view
    filter = None

    # Make this view require the appropriate permission
    @property
    def permission_required(self):
        return self.get_full_perm_name(self.perm_name)

    # Given a short permission name like 'change' or 'add', return
    # the full name like 'app_label.change_model' for this view's model.
    def get_full_perm_name(self, short_name):
        return "{app_name}.{perm_name}_{model_name}".format(
            app_name=self.bread.model._meta.app_label,
            model_name=self.bread.model._meta.object_name.lower(),
            perm_name=short_name,
        )

    def __init__(self, *args, **kwargs):
        # Make sure the permission needed to use this view exists.
        super(BreadViewMixin, self).__init__(*args, **kwargs)
        perm_name = '%s_%s' % (self.perm_name, self.bread.model._meta.object_name.lower())
        perm = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(self.bread.model),
            codename=perm_name
        ).first()
        if not perm:
            raise ImproperlyConfigured(
                "The view %r requires permission %s but there's no such permission"
                % (self, perm_name)
            )

    # Override dispatch to get our own custom version of the braces
    # PermissionRequired mixin.  Here's how ours behaves:
    #
    # If user is not logged in, redirect to a login page.
    # Else, if user does not have the required permission, return 403.
    # Else, carry on.
    def dispatch(self, request, *args, **kwargs):
        # Make sure that the permission_required attribute is set on the
        # view, or raise a configuration error.
        if self.permission_required is None:   # pragma: no cover
            raise ImproperlyConfigured(
                "'BreadViewMixin' requires "
                "'permission_required' attribute to be set.")

        # Check if the user is logged in
        if not request.user.is_authenticated():
            return redirect_to_login(request.get_full_path(),
                                     settings.LOGIN_URL,
                                     REDIRECT_FIELD_NAME)

        # Check to see if the request's user has the required permission.
        has_permission = request.user.has_perm(self.permission_required)

        if not has_permission:  # If the user lacks the permission
            raise PermissionDenied  # return a forbidden response.

        return super(BreadViewMixin, self).dispatch(request, *args, **kwargs)

    def get_paginate_by(self):
        return self.bread.paginate_by

    def get_template_names(self):
        # Is there a template_name_pattern?
        if self.bread.template_name_pattern:
            return [self.bread.template_name_pattern.format(
                app_label=self.bread.model._meta.app_label,
                model=self.bread.model._meta.object_name.lower(),
                view=self.template_name_suffix
            )]
        # First try the default names for Django Vanilla views, then
        # add on 'bread/<viewname>.html' as a final possibility.
        return (super(BreadViewMixin, self).get_template_names()
                + ['bread/%s.html' % self.template_name_suffix])

    def _get_new_url(self, **query_parms):
        """Return a new URL consisting of this request's URL, with any specified
        query parms updated or added"""
        request_kwargs = dict(self.request.GET)
        request_kwargs.update(query_parms)
        return self.request.path + "?" + urlencode(request_kwargs, doseq=True)

    def get_context_data(self, **kwargs):
        data = super(BreadViewMixin, self).get_context_data(**kwargs)
        # Include reference to the Bread object in template contexts
        data['bread'] = self.bread
        data['columns'] = self.bread.columns
        if data.get('is_paginated', False):
            page = data['page_obj']
            num_pages = data['paginator'].num_pages
            if page.has_next():
                if page.next_page_number() != num_pages:
                    data['next_url'] = self._get_new_url(page=page.next_page_number())
                data['last_url'] = self._get_new_url(page=num_pages)
            if page.has_previous():
                data['first_url'] = self._get_new_url(page=1)
                if page.previous_page_number() != 1:
                    data['previous_url'] = self._get_new_url(page=page.previous_page_number())

        # Template that the default bread templates should extend
        data['base_template'] = self.bread.base_template

        data['filter'] = self.filter

        # Add 'may_<viewname>' to the context for each view, so the templates can
        # tell if the current user may use the named view.
        data['may_browse'] = 'B' in self.bread.views \
                             and self.request.user.has_perm(self.get_full_perm_name('browse'))
        data['may_read'] = 'R' in self.bread.views \
                           and self.request.user.has_perm(self.get_full_perm_name('read'))
        data['may_edit'] = 'E' in self.bread.views \
                           and self.request.user.has_perm(self.get_full_perm_name('change'))
        data['may_add'] = 'A' in self.bread.views \
                          and self.request.user.has_perm(self.get_full_perm_name('add'))
        data['may_delete'] = 'D' in self.bread.views \
                             and self.request.user.has_perm(self.get_full_perm_name('delete'))
        return data

    def get_form(self, data=None, files=None, **kwargs):
        if not self.form_class:
            self.form_class = modelform_factory(
                self.bread.model,
                fields='__all__',
                exclude=self.bread.exclude
            )
        return self.form_class(data=data, files=files, **kwargs)

    @property
    def success_url(self):
        return reverse_lazy(self.bread.browse_url_name())


# The individual view classes we'll use and customize in the
# omnibus class below:
class BrowseView(BreadViewMixin, ListView):
    perm_name = 'browse'  # Not a default Django permission
    template_name_suffix = 'browse'

    def get_queryset(self):
        qset = super(BrowseView, self).get_queryset()

        # Now filter
        if self.bread.filter:
            self.filter = self.bread.filter(self.request.GET, queryset=qset)
            qset = self.filter.qs

        return qset


class ReadView(BreadViewMixin, DetailView):
    """
    The read view makes a form, not because we're going to submit
    changes, but just as a handy container for the object's data that
    we can iterate over in the template to display it if we don't want
    to make a custom template for this model.
    """
    perm_name = 'read'  # Not a default Django permission
    template_name_suffix = 'read'

    def get_context_data(self, **kwargs):
        data = super(ReadView, self).get_context_data(**kwargs)
        data['form'] = self.get_form(instance=self.object)
        return data


class EditView(BreadViewMixin, UpdateView):
    perm_name = 'change'  # Default Django permission
    template_name_suffix = 'edit'

    def form_invalid(self, form):
        # Return a 400 if the form isn't valid
        rsp = super(EditView, self).form_invalid(form)
        rsp.status_code = BAD_REQUEST
        return rsp


class AddView(BreadViewMixin, CreateView):
    perm_name = 'add'  # Default Django permission
    template_name_suffix = 'edit'  # Yes 'edit' not 'add'

    def form_invalid(self, form):
        # Return a 400 if the form isn't valid
        rsp = super(AddView, self).form_invalid(form)
        rsp.status_code = BAD_REQUEST
        return rsp


class DeleteView(BreadViewMixin, DeleteView):
    perm_name = 'delete'  # Default Django permission
    template_name_suffix = 'delete'


class Bread(object):
    """
    Provide a set of BREAD views for a model.

    Example usage:

        bread_views_for_model = Bread(Model, other kwargs...)
        ...
        urlpatterns += bread_views_for_model.get_urls()

    See `get_urls` for the resulting URL names and paths.

    You could subclass Bread if you need to customize it a lot, but it
    is intended that most customization can be done by passing parameters
    to the constructor.

    Below, <name> refers to the lowercased model name, e.g. 'model'.

    Each view requires a permission. The expected permissions are named:

    * browse_<name>   (not a default Django permission)
    * read_<name>   (not a default Django permission)
    * change_<name>    (this is a default Django permission, used on the Edit view)
    * add_<name>    (this is a default Django permission)
    * delete_<name>    (this is a default Django permission)

    Parameters:

    model (required): The model class

    plural_name (optional): Override just adding 's' to the lowercased name
        of the model to form the plural

    form_class (optional): override the custom form class we're using for this model

    exclude (optional): list of names of fields not to include in the form

    base_XXX_view_class (optional): override the base view classes

    columns (optional): List of ('Title', 'attrname') pairs to customize the columns
    in the browse view. 'attrname' may include '__' to drill down into fields,
    e.g. 'user__name' to get the user's name, or 'type__get_number_display' to
    call get_number_display() on the object from the type field.  (Assumes
    the default template, obviously).

    paginate_by (optional): Limit browsing to this many items per page, and add controls
    to navigate among pages.

    views (optional): Pass a string containing the first letters of the views to include.
    Default is 'BREAD'.  Any omitted views will not have URLs defined and so will
    not be accessible.

    filter (optional): form class to use to control filtering. Must be a subclass
    of django-filters' `django_filters.FilterSet` class.

    Assumes templates with the following names:

        Browse - <app>/<name>_browse.html
        Read   - <app>/<name>_read.html
        Edit   - <app>/<name>_edit.html
        Add    - <app>/<name>_add.html
        Delete - <app>/<name>_confirm_delete.html

    but defaults to bread/<activity>.html if those aren't found.  The bread/<activity>.html
    templates are very generic, but you can pass 'base_template' as the name of a template
    that they should extend. They will supply `{% block title %}` and `{% block content %}`.

    OR, you can pass in template_name_pattern as a string that will be used to come up with
    a template name by substituting `{app_label}`, `{model}` (lower-cased model name), and
    `{view}` (`browse`, `read`, etc.).

    """
    base_browse_view_class = BrowseView
    base_read_view_class = ReadView
    base_edit_view_class = EditView
    base_add_view_class = AddView
    base_delete_view_class = DeleteView

    exclude = []  # Names of fields not to show
    columns = []
    paginate_by = None
    views = "BREAD"
    base_template = None
    url_namespace = ''

    def __init__(self,
                 model,
                 plural_name=None,
                 form_class=None,
                 exclude=None,
                 base_browse_view_class=None,
                 base_read_view_class=None,
                 base_edit_view_class=None,
                 base_add_view_class=None,
                 base_delete_view_class=None,
                 columns=None,
                 paginate_by=None,
                 views="BREAD",
                 base_template=None,
                 filter=None,
                 template_name_pattern=None,
                 url_namespace='',
                 ):
        if exclude is not None and form_class is not None:
            raise ImproperlyConfigured(
                "exclude and form_class are mutually exclusive - if you're overrding the form, "
                "just specify the excluded fields there."
            )
        self.model = model
        self.name = self.model._meta.object_name.lower()
        self.plural_name = plural_name or self.name + 's'
        self.form_class = form_class
        self.exclude = exclude or self.exclude
        self.base_browse_view_class = base_browse_view_class or self.base_browse_view_class
        self.base_read_view_class = base_read_view_class or self.base_read_view_class
        self.base_edit_view_class = base_edit_view_class or self.base_edit_view_class
        self.base_add_view_class = base_add_view_class or self.base_add_view_class
        self.base_delete_view_class = base_delete_view_class or self.base_delete_view_class
        self.columns = columns
        self.paginate_by = paginate_by
        self.views = views.upper()
        self.base_template = base_template or setting('DEFAULT_BASE_TEMPLATE', 'base.html')
        self.filter = filter
        self.template_name_pattern = (template_name_pattern
                                      or setting('DEFAULT_TEMPLATE_NAME_PATTERN', None))
        self.url_namespace = url_namespace

    #####
    # B #
    #####
    def browse_url_name(self, include_namespace=True):
        """Return the URL name for browsing this model"""
        return self.get_url_name('browse', include_namespace)

    def get_browse_view(self):
        """Return a view method for browsing."""

        return self.base_browse_view_class.as_view(
            bread=self,
            model=self.model,
        )

    #####
    # R #
    #####
    def read_url_name(self, include_namespace=True):
        return self.get_url_name('read', include_namespace)

    def get_read_view(self):
        return self.base_read_view_class.as_view(
            bread=self,
            model=self.model,
            form_class=self.form_class,
        )

    #####
    # E #
    #####
    def edit_url_name(self, include_namespace=True):
        return self.get_url_name('edit', include_namespace)

    def get_edit_view(self):
        return self.base_edit_view_class.as_view(
            bread=self,
            model=self.model,
            form_class=self.form_class,
        )

    #####
    # A #
    #####
    def add_url_name(self, include_namespace=True):
        return self.get_url_name('add', include_namespace)

    def get_add_view(self):
        return self.base_add_view_class.as_view(
            bread=self,
            model=self.model,
            form_class=self.form_class,
        )

    #####
    # D #
    #####
    def delete_url_name(self, include_namespace=True):
        return self.get_url_name('delete', include_namespace)

    def get_delete_view(self):
        return self.base_delete_view_class.as_view(
            bread=self,
            model=self.model,
        )

    ##########
    # Common #
    ##########
    def get_url_name(self, view_name, include_namespace=True):
        if include_namespace:
            url_namespace = self.url_namespace + ':' if self.url_namespace else ''
        else:
            url_namespace = ''
        if view_name == 'browse':
            return '%s%s_%ss' % (url_namespace, view_name, self.name)
        else:
            return '%s%s_%s' % (url_namespace, view_name, self.name)

    def get_urls(self):
        """
        Return urlpatterns to add for this model's BREAD interface.

        These will be of the form:

           Operation    Name                   URL
           ---------    --------------------   --------------------------
           Browse       browse_<plural_name>   <plural_name>/
           Read         read_<name>            <plural_name>/<pk>/
           Edit         edit_<name>            <plural_name>/<pk>/edit/
           Add          add_<name>             <plural_name>/add/
           Delete       delete_<name>          <plural_name>/<pk>/delete/

        Example usage:

            urlpatterns += my_bread.get_urls()

        If a restricted set of views is passed in the 'views' parameter, then
        only URLs for those views will be included.
        """

        urlpatterns = []
        if 'B' in self.views:
            urlpatterns.append(
                url(r'^%s/$' % self.plural_name,
                    self.get_browse_view(),
                    name=self.browse_url_name(include_namespace=False)))

        if 'R' in self.views:
            urlpatterns.append(
                url(r'^%s/(?P<pk>\d+)/$' % self.plural_name,
                    self.get_read_view(),
                    name=self.read_url_name(include_namespace=False)))

        if 'E' in self.views:
            urlpatterns.append(
                url(r'^%s/(?P<pk>\d+)/edit/$' % self.plural_name,
                    self.get_edit_view(),
                    name=self.edit_url_name(include_namespace=False)))

        if 'A' in self.views:
            urlpatterns.append(
                url(r'^%s/add/$' % self.plural_name,
                    self.get_add_view(),
                    name=self.add_url_name(include_namespace=False)))

        if 'D' in self.views:
            urlpatterns.append(
                url(r'^%s/(?P<pk>\d+)/delete/$' % self.plural_name,
                    self.get_delete_view(),
                    name=self.delete_url_name(include_namespace=False)))
        return urlpatterns
