from httplib import OK, METHOD_NOT_ALLOWED
from django.core.urlresolvers import reverse
from bread.tests.base import BreadTestCase
from bread.tests.factories import BreadTestModelFactory


class BreadBrowseTest(BreadTestCase):
    def test_get(self):
        self.set_urls(self.bread)
        items = [BreadTestModelFactory() for __ in range(5)]
        self.give_permission('browse')
        url = reverse(self.bread.get_url_name('browse'))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(OK, rsp.status_code)
        rsp.render()
        body = rsp.content.decode('utf-8')
        for item in items:
            self.assertIn(item.name, body)

    def test_get_empty_list(self):
        self.set_urls(self.bread)
        self.model.objects.all().delete()
        self.give_permission('browse')
        url = reverse(self.bread.get_url_name('browse'))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(OK, rsp.status_code)

    def test_post(self):
        self.set_urls(self.bread)
        self.give_permission('browse')
        url = reverse(self.bread.get_url_name('browse'))
        request = self.request_factory.post(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(METHOD_NOT_ALLOWED, rsp.status_code)
