try:
    from httplib import FOUND, BAD_REQUEST, OK
except ImportError:
    from http.client import FOUND, BAD_REQUEST, OK
from django.core.urlresolvers import reverse

from .base import BreadTestCase


class BreadEditTest(BreadTestCase):
    def setUp(self):
        super(BreadEditTest, self).setUp()
        self.set_urls(self.bread)

    def test_edit_item(self):
        item = self.model_factory()
        url = reverse(self.bread.get_url_name('edit'), kwargs={'pk': item.pk})
        request = self.request_factory.post(url, data={'name': 'Fred Jones'})
        request.user = self.user
        self.give_permission('change')
        view = self.bread.get_edit_view()
        rsp = view(request, pk=item.pk)
        self.assertEqual(FOUND, rsp.status_code)
        self.assertEqual(reverse(self.bread.get_url_name('browse')), rsp['Location'])
        item = self.model.objects.get(pk=item.pk)
        self.assertEqual('Fred Jones', item.name)

    def test_fail_validation(self):
        item = self.model_factory()
        url = reverse(self.bread.get_url_name('edit'), kwargs={'pk': item.pk})
        request = self.request_factory.post(url, data={'name': 'this name is too much long yeah'})
        request.user = self.user
        self.give_permission('change')
        view = self.bread.get_edit_view()
        rsp = view(request, pk=item.pk)
        self.assertEqual(BAD_REQUEST, rsp.status_code)
        context = rsp.context_data
        form = context['form']
        errors = form.errors
        self.assertIn('name', errors)

    def test_get(self):
        # Get should give you a form with the item filled in
        item = self.model_factory()
        url = reverse(self.bread.get_url_name('edit'), kwargs={'pk': item.pk})
        request = self.request_factory.get(url)
        request.user = self.user
        self.give_permission('change')
        view = self.bread.get_edit_view()
        rsp = view(request, pk=item.pk)
        self.assertEqual(OK, rsp.status_code)
        form = rsp.context_data['form']
        self.assertFalse(form.is_bound)
        self.assertEqual(item.pk, form.initial['id'])
        self.assertEqual(item.name, form.initial['name'])
        rsp.render()
        body = rsp.content.decode('utf-8')
        self.assertIn('method="POST"', body)
