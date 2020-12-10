from django.http import Http404
from django.urls import reverse

from .base import BreadTestCase


class BreadDeleteTest(BreadTestCase):
    def setUp(self):
        super(BreadDeleteTest, self).setUp()
        self.set_urls(self.bread)

    def test_delete_item(self):
        self.item = self.model_factory()
        url = reverse(self.bread.get_url_name("delete"), kwargs={"pk": self.item.pk})
        self.give_permission("delete")

        # Get should work and give us a confirmation page
        request = self.request_factory.get(url)
        request.user = self.user
        view = self.bread.get_delete_view()
        rsp = view(request, pk=self.item.pk)
        self.assertTrue(rsp.context_data["bread_test_class"])
        self.assertEqual(200, rsp.status_code)
        self.assertTrue(self.model.objects.filter(pk=self.item.pk).exists())

        # Now post to confirm
        request = self.request_factory.post(url)
        request.user = self.user
        view = self.bread.get_delete_view()
        rsp = view(request, pk=self.item.pk)
        self.assertEqual(302, rsp.status_code)
        self.assertEqual(reverse(self.bread.get_url_name("browse")), rsp["Location"])
        self.assertFalse(self.model.objects.filter(pk=self.item.pk).exists())

    def test_delete_nonexistent_item(self):
        url = reverse(self.bread.get_url_name("delete"), kwargs={"pk": 999})
        self.give_permission("delete")

        # Get should not work - 404
        request = self.request_factory.get(url)
        request.user = self.user
        view = self.bread.get_delete_view()
        with self.assertRaises(Http404):
            view(request, pk=999)

        # Same for post
        request = self.request_factory.post(url)
        request.user = self.user
        view = self.bread.get_delete_view()
        with self.assertRaises(Http404):
            view(request, pk=999)
