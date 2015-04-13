try:
    from httplib import OK, METHOD_NOT_ALLOWED
except ImportError:
    from http.client import OK, METHOD_NOT_ALLOWED
from django.core.urlresolvers import reverse
from django.http import Http404
from bread.bread import Bread
from .base import BreadTestCase


class BreadPaginationTest(BreadTestCase):
    page_size = 5

    def setUp(self):
        super(BreadPaginationTest, self).setUp()
        self.bread = Bread(model=self.model, base_template='bread/empty.html',
                           paginate_by=self.page_size)
        [self.model_factory() for __ in range(2 * self.page_size + 1)]
        self.set_urls(self.bread)
        self.give_permission('browse')

    def test_get(self):
        url = reverse(self.bread.get_url_name('browse'))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(OK, rsp.status_code)
        rsp.render()
        context = rsp.context_data
        object_list = context['object_list']
        self.assertEqual(self.page_size, len(object_list))
        paginator = context['paginator']
        self.assertEqual(3, paginator.num_pages)
        # Should start with first item
        ordered_items = self.model.objects.all()
        self.assertEqual(object_list[0], ordered_items[0])

    def test_get_second_page(self):
        url = reverse(self.bread.get_url_name('browse')) + "?page=2"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(OK, rsp.status_code)
        rsp.render()
        context = rsp.context_data
        object_list = context['object_list']
        self.assertEqual(self.page_size, len(object_list))
        paginator = context['paginator']
        self.assertEqual(3, paginator.num_pages)
        # Should start with item with index page_size
        ordered_items = self.model.objects.all()
        self.assertEqual(object_list[0], ordered_items[self.page_size])

    def test_get_page_past_the_end(self):
        url = reverse(self.bread.get_url_name('browse')) + "?page=99"
        request = self.request_factory.get(url)
        request.user = self.user
        with self.assertRaises(Http404):
            self.bread.get_browse_view()(request)

    def test_get_empty_list(self):
        self.set_urls(self.bread)
        self.model.objects.all().delete()
        self.give_permission('browse')
        url = reverse(self.bread.get_url_name('browse'))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(OK, rsp.status_code)
        context = rsp.context_data
        paginator = context['paginator']
        self.assertEqual(1, paginator.num_pages)
        self.assertEqual(0, len(context['object_list']))

    def test_post(self):
        self.set_urls(self.bread)
        self.give_permission('browse')
        url = reverse(self.bread.get_url_name('browse'))
        request = self.request_factory.post(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(METHOD_NOT_ALLOWED, rsp.status_code)
