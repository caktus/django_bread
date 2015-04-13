try:
    from httplib import OK, METHOD_NOT_ALLOWED
except ImportError:
    from http.client  import OK, METHOD_NOT_ALLOWED

from django.core.urlresolvers import reverse
from django.http import Http404

from .base import BreadTestCase


class BreadReadTest(BreadTestCase):
    def setUp(self):
        super(BreadReadTest, self).setUp()
        self.urlconf = 'bread.tests.test_read'
        self.give_permission('read')
        self.set_urls(self.bread)

    def test_read(self):
        item = self.model_factory()
        url = reverse('read_%s' % self.model_name, kwargs={'pk': item.pk})
        request = self.request_factory.get(url)
        request.user = self.user

        view = self.bread.get_read_view()
        rsp = view(request, pk=item.pk)

        self.assertEqual(OK, rsp.status_code)
        rsp.render()
        body = rsp.content.decode('utf-8')
        self.assertIn(item.name, body)

    def test_read_no_such_item(self):
        self.assertFalse(self.model.objects.filter(pk=999).exists())
        url = reverse('read_%s' % self.model_name, kwargs={'pk': 999})
        request = self.request_factory.get(url)
        request.user = self.user

        view = self.bread.get_read_view()
        with self.assertRaises(Http404):
            view(request, pk=999)

    def test_post(self):
        self.set_urls(self.bread)
        self.give_permission('read')
        item = self.model_factory()
        url = reverse(self.bread.get_url_name('read'), kwargs={'pk': item.pk})
        request = self.request_factory.post(url)
        request.user = self.user
        rsp = self.bread.get_read_view()(request)
        self.assertEqual(METHOD_NOT_ALLOWED, rsp.status_code)
