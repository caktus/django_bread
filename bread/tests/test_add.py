from httplib import FOUND, BAD_REQUEST, OK
from django.core.urlresolvers import reverse
from bread.tests.base import BreadTestCase


class BreadAddTest(BreadTestCase):
    def setUp(self):
        super(BreadAddTest, self).setUp()
        self.set_urls(self.bread)

    def test_new_item(self):
        self.model.objects.all().delete()
        url = reverse(self.bread.get_url_name('add'))
        request = self.request_factory.post(url, data={'name': 'Fred Jones'})
        request.user = self.user
        self.give_permission('add')
        view = self.bread.get_add_view()
        rsp = view(request)
        self.assertEqual(FOUND, rsp.status_code)
        self.assertEqual(reverse(self.bread.get_url_name('browse')), rsp['Location'])
        item = self.model.objects.get()
        self.assertEqual('Fred Jones', item.name)

    def test_fail_validation(self):
        self.model.objects.all().delete()
        url = reverse(self.bread.get_url_name('add'))
        request = self.request_factory.post(url, data={'name': 'this name is too much long yeah'})
        request.user = self.user
        self.give_permission('add')
        view = self.bread.get_add_view()
        rsp = view(request)
        self.assertEqual(BAD_REQUEST, rsp.status_code)
        context = rsp.context_data
        form = context['form']
        errors = form.errors
        self.assertIn('name', errors)

    def test_get(self):
        # Get should give you a blank form
        url = reverse(self.bread.get_url_name('add'))
        request = self.request_factory.get(url)
        request.user = self.user
        self.give_permission('add')
        view = self.bread.get_add_view()
        rsp = view(request)
        self.assertEqual(OK, rsp.status_code)
        form = rsp.context_data['form']
        self.assertFalse(form.is_bound)
        rsp.render()
        body = rsp.content.decode('utf-8')
        self.assertIn('method="POST"', body)
