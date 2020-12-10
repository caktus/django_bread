from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import override_settings
from django.urls import reverse

from .base import BreadTestCase


class BreadPermissionTestMixin(object):
    # Just a mixin so these test methods don't try to run on
    # a parent testcase class
    include_post = False

    def setUp(self):
        super(BreadPermissionTestMixin, self).setUp()

        self.set_urls(self.bread)

        self.item = self.model_factory()
        url_name = self.bread.get_url_name(self.view_name)
        if self.expects_pk:
            url = reverse(url_name, kwargs={"pk": self.item.pk})
        else:
            url = reverse(url_name)
        self.request = self.request_factory.get(url)
        self.request.user = self.user

        self.post_request = self.request_factory.post(url, {"name": "foo"})
        self.post_request.user = self.user

        view_getter = getattr(self.bread, "get_%s_view" % self.view_name)
        self.view = view_getter()

    @override_settings(LOGIN_URL="/logmein")
    def test_when_not_logged_in(self):
        # Can't do it if not logged in
        # but we get redirected rather than PermissionDenied
        self.request.user = AnonymousUser()
        rsp = self.view(self.request, pk=self.item.pk)
        expected_url = "%s?%s=%s" % (
            settings.LOGIN_URL,
            REDIRECT_FIELD_NAME,
            self.request.path,
        )
        self.assertEqual(expected_url, rsp["Location"])

        if self.include_post:
            self.post_request.user = AnonymousUser()
            rsp = self.view(self.post_request, pk=self.item.pk)
            self.assertEqual(302, rsp.status_code)
            self.assertEqual(expected_url, rsp["Location"])

    def test_access_without_permission(self):
        # Can't do it when logged in but no permission, get 403
        with self.assertRaises(PermissionDenied):
            if self.expects_pk:
                self.view(self.request, pk=self.item.pk)
            else:
                self.view(self.request)
        if self.include_post:
            with self.assertRaises(PermissionDenied):
                if self.expects_pk:
                    self.view(self.post_request, pk=self.item.pk)
                else:
                    self.view(self.post_request)


class BreadBrowsePermissionTest(BreadPermissionTestMixin, BreadTestCase):
    view_name = "browse"
    expects_pk = False


class BreadReadPermissionTest(BreadPermissionTestMixin, BreadTestCase):
    view_name = "read"
    expects_pk = True


class BreadEditPermissionTest(BreadPermissionTestMixin, BreadTestCase):
    view_name = "edit"
    expects_pk = True
    include_post = True


class BreadAddPermissionTest(BreadPermissionTestMixin, BreadTestCase):
    view_name = "add"
    expects_pk = False
    include_post = True


class BreadDeletePermissionTest(BreadPermissionTestMixin, BreadTestCase):
    view_name = "read"
    expects_pk = True
    include_post = True
