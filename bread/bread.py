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
from django.db.models import Model
from django.forms.models import modelform_factory
from vanilla import ListView, DetailView, CreateView, UpdateView, DeleteView

from .utils import validate_fieldspec


"""
About settings.

You can provide a Django setting named BREAD as a dictionary.
Here are the settings, all currently optional:

DEFAULT_BASE_TEMPLATE: Default value for Bread's base_template argument
"""


# Helper to get settings from BREAD dictionary, or default
def setting(name, default=None):
    BREAD = getattr(settings, 'BREAD', {})
    return BREAD.get(name, default)


class BreadViewMixin(object):
    """We mix this into all the views for some common features"""
    bread = None  # The Bread object using this view

    exclude = None
    form_class = None

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

    def get_template_names(self):
        """Return Django Vanilla templates (app-specific), then
                  Customized template via Bread object, then
                  Django Bread template
        """
        vanilla_templates = super(BreadViewMixin, self).get_template_names()

        # template_name_suffix may have a leading underscore (to make it work well with Django
        # Vanilla Views). If it does, then we strip the underscore to get our 'view' name.
        # e.g. template_name_suffix '_browse' -> view 'browse'
        suffix = self.template_name_suffix
        view = suffix[1:] if suffix.startswith('_') else suffix
        default_template = 'bread/%s.html' % view
        if self.bread.template_name_pattern:
            custom_template = self.bread.template_name_pattern.format(
                app_label=self.bread.model._meta.app_label,
                model=self.bread.model._meta.object_name.lower(),
                view=view
            )
            return vanilla_templates + [custom_template] + [default_template]
        return vanilla_templates + [default_template]

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

        # Provide references to useful Model Meta attributes
        data['verbose_name'] = self.model._meta.verbose_name
        data['verbose_name_plural'] = self.model._meta.verbose_name_plural

        # Template that the default bread templates should extend
        data['base_template'] = self.bread.base_template

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
        form_class = self.form_class or self.bread.form_class
        if not form_class:
            form_class = modelform_factory(
                self.bread.model,
                fields='__all__',
                exclude=self.exclude or self.bread.exclude
            )
        return form_class(data=data, files=files, **kwargs)

    @property
    def success_url(self):
        return reverse_lazy(self.bread.browse_url_name())


# The individual view classes we'll use and customize in the
# omnibus class below:
class BrowseView(BreadViewMixin, ListView):
    # Configurable:
    columns = []
    filterset = None  # Class
    paginate_by = None
    perm_name = 'browse'  # Not a default Django permission
    template_name_suffix = '_browse'

    def __init__(self, *args, **kwargs):
        super(BrowseView, self).__init__(*args, **kwargs)
        # Internal use
        self.filter = None

    def get_queryset(self):
        qset = super(BrowseView, self).get_queryset()

        # Now filter
        if self.filterset is not None:
            self.filter = self.filterset(self.request.GET, queryset=qset)
            qset = self.filter.qs
        return qset

    def get_context_data(self, **kwargs):
        data = super(BrowseView, self).get_context_data(**kwargs)
        data['columns'] = self.columns
        data['filter'] = self.filter
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
        return data


class ReadView(BreadViewMixin, DetailView):
    """
    The read view makes a form, not because we're going to submit
    changes, but just as a handy container for the object's data that
    we can iterate over in the template to display it if we don't want
    to make a custom template for this model.
    """
    perm_name = 'read'  # Not a default Django permission
    template_name_suffix = '_read'

    def get_context_data(self, **kwargs):
        data = super(ReadView, self).get_context_data(**kwargs)
        data['form'] = self.get_form(instance=self.object)
        return data


class EditView(BreadViewMixin, UpdateView):
    perm_name = 'change'  # Default Django permission
    template_name_suffix = '_edit'

    def form_invalid(self, form):
        # Return a 400 if the form isn't valid
        rsp = super(EditView, self).form_invalid(form)
        rsp.status_code = BAD_REQUEST
        return rsp


class AddView(BreadViewMixin, CreateView):
    perm_name = 'add'  # Default Django permission
    template_name_suffix = '_edit'  # Yes 'edit' not 'add'

    def form_invalid(self, form):
        # Return a 400 if the form isn't valid
        rsp = super(AddView, self).form_invalid(form)
        rsp.status_code = BAD_REQUEST
        return rsp


class DeleteView(BreadViewMixin, DeleteView):
    perm_name = 'delete'  # Default Django permission
    template_name_suffix = '_delete'


class Bread(object):
    """
    Provide a set of BREAD views for a model.

    Example usage:

        bread_views_for_model = Bread(Model, other kwargs...)
        ...
        urlpatterns += bread_views_for_model.get_urls()

    See `get_urls` for the resulting URL names and paths.

    It is expected that you subclass `Bread` and customize it by at least
    setting attributes on the subclass.

    Below, <name> refers to the lowercased model name, e.g. 'model'.

    Each view requires a permission. The expected permissions are named:

    * browse_<name>   (not a default Django permission)
    * read_<name>   (not a default Django permission)
    * change_<name>    (this is a default Django permission, used on the Edit view)
    * add_<name>    (this is a default Django permission)
    * delete_<name>    (this is a default Django permission)

    Parameters:

    Assumes templates with the following names:

        Browse - <app>/<name>browse.html
        Read   - <app>/<name>read.html
        Edit   - <app>/<name>edit.html
        Add    - <app>/<name>add.html
        Delete - <app>/<name>delete.html

    but defaults to bread/<activity>.html if those aren't found.  The bread/<activity>.html
    templates are very generic, but you can pass 'base_template' as the name of a template
    that they should extend. They will supply `{% block title %}` and `{% block content %}`.

    OR, you can pass in template_name_pattern as a string that will be used to come up with
    a template name by substituting `{app_label}`, `{model}` (lower-cased model name), and
    `{view}` (`browse`, `read`, etc.).

    """
    browse_view = BrowseView
    read_view = ReadView
    edit_view = EditView
    add_view = AddView
    delete_view = DeleteView

    exclude = []  # Names of fields not to show
    views = "BREAD"
    base_template = setting('DEFAULT_BASE_TEMPLATE', 'base.html')
    namespace = ''
    template_name_pattern = None
    plural_name = None
    form_class = None

    def __init__(self):
        self.name = self.model._meta.object_name.lower()
        self.views = self.views.upper()

        if not self.plural_name:
            self.plural_name = self.name + 's'

        if not issubclass(self.model, Model):
            raise TypeError("'model' argument for Bread must be a "
                            "subclass of Model; it is %r" % self.model)

        if self.browse_view.columns:
            for title, column in self.browse_view.columns:
                validate_fieldspec(self.model, column)

        if hasattr(self, 'paginate_by') or hasattr(self, 'columns'):
            raise ValueError("The 'paginate_by' and 'columns' settings have been moved "
                             "from the Bread class to the BrowseView class.")
        if hasattr(self, 'filter'):
            raise ValueError("The 'filter' setting has been renamed to 'filterset' and moved "
                             "to the BrowseView.")
        if hasattr(self, 'filterset'):
            raise ValueError("The 'filterset' setting should be on the BrowseView, not "
                             "the Bread view.")

    #####
    # B #
    #####
    def browse_url_name(self, include_namespace=True):
        """Return the URL name for browsing this model"""
        return self.get_url_name('browse', include_namespace)

    def get_browse_view(self):
        """Return a view method for browsing."""

        return self.browse_view.as_view(
            bread=self,
            model=self.model,
        )

    #####
    # R #
    #####
    def read_url_name(self, include_namespace=True):
        return self.get_url_name('read', include_namespace)

    def get_read_view(self):
        return self.read_view.as_view(
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
        return self.edit_view.as_view(
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
        return self.add_view.as_view(
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
        return self.delete_view.as_view(
            bread=self,
            model=self.model,
        )

    ##########
    # Common #
    ##########
    def get_url_name(self, view_name, include_namespace=True):
        if include_namespace:
            url_namespace = self.namespace + ':' if self.namespace else ''
        else:
            url_namespace = ''
        if view_name == 'browse':
            return '%s%s_%s' % (url_namespace, view_name, self.plural_name)
        else:
            return '%s%s_%s' % (url_namespace, view_name, self.name)

    def get_urls(self, prefix=True):
        """
        Return urlpatterns to add for this model's BREAD interface.

        By default, these will be of the form:

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

        If prefix is False, ``<plural_name>/`` will not be included on
        the front of the URLs.

        """

        prefix = '%s/' % self.plural_name if prefix else ''

        urlpatterns = []
        if 'B' in self.views:
            urlpatterns.append(
                url(r'^%s$' % prefix,
                    self.get_browse_view(),
                    name=self.browse_url_name(include_namespace=False)))

        if 'R' in self.views:
            urlpatterns.append(
                url(r'^%s(?P<pk>\d+)/$' % prefix,
                    self.get_read_view(),
                    name=self.read_url_name(include_namespace=False)))

        if 'E' in self.views:
            urlpatterns.append(
                url(r'^%s(?P<pk>\d+)/edit/$' % prefix,
                    self.get_edit_view(),
                    name=self.edit_url_name(include_namespace=False)))

        if 'A' in self.views:
            urlpatterns.append(
                url(r'^%sadd/$' % prefix,
                    self.get_add_view(),
                    name=self.add_url_name(include_namespace=False)))

        if 'D' in self.views:
            urlpatterns.append(
                url(r'^%s(?P<pk>\d+)/delete/$' % prefix,
                    self.get_delete_view(),
                    name=self.delete_url_name(include_namespace=False)))
        return urlpatterns
