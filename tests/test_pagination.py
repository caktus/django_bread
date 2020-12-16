from django.http import Http404
from django.urls import reverse

from bread.bread import BrowseView

from .base import BreadTestCase

PAGE_SIZE = 5


class BreadPaginationTest(BreadTestCase):
    class BrowseTestView(BrowseView):
        paginate_by = PAGE_SIZE

    extra_bread_attributes = {"browse_view": BrowseTestView}

    def setUp(self):
        super(BreadPaginationTest, self).setUp()
        [self.model_factory() for __ in range(2 * PAGE_SIZE + 1)]
        self.set_urls(self.bread)
        self.give_permission("browse")

    def test_get(self):
        url = reverse(self.bread.get_url_name("browse"))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        context = rsp.context_data
        object_list = context["object_list"]
        self.assertEqual(PAGE_SIZE, len(object_list))
        paginator = context["paginator"]
        self.assertEqual(3, paginator.num_pages)
        # Should start with first item
        ordered_items = self.model.objects.all()
        self.assertEqual(object_list[0], ordered_items[0])

    def test_get_second_page(self):
        url = reverse(self.bread.get_url_name("browse")) + "?page=2"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        context = rsp.context_data
        object_list = context["object_list"]
        self.assertEqual(PAGE_SIZE, len(object_list))
        paginator = context["paginator"]
        self.assertEqual(3, paginator.num_pages)
        # Should start with item with index page_size
        ordered_items = self.model.objects.all()
        self.assertEqual(object_list[0], ordered_items[PAGE_SIZE])

    def test_get_page_past_the_end(self):
        url = reverse(self.bread.get_url_name("browse")) + "?page=99"
        request = self.request_factory.get(url)
        request.user = self.user
        with self.assertRaises(Http404):
            self.bread.get_browse_view()(request)

    def test_get_empty_list(self):
        self.set_urls(self.bread)
        self.model.objects.all().delete()
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse"))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        context = rsp.context_data
        paginator = context["paginator"]
        self.assertEqual(1, paginator.num_pages)
        self.assertEqual(0, len(context["object_list"]))

    def test_post(self):
        self.set_urls(self.bread)
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse"))
        request = self.request_factory.post(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(405, rsp.status_code)

    def test_next_url(self):
        # Make sure next_url includes other query params unaltered
        self.set_urls(self.bread)
        self.give_permission("browse")
        base_url = reverse(self.bread.get_url_name("browse"))
        # Add a query parm that needs to be preserved by the next page link
        url = base_url + "?test=1"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        context = rsp.context_data
        next_url = context["next_url"]
        # We don't know what order the query parms will end up in
        expected_urls = [base_url + "?test=1&page=2", base_url + "?page=2&test=1"]
        self.assertIn(next_url, expected_urls)
