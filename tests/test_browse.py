import json
from unittest.mock import patch

from django.urls import reverse

from bread.bread import BrowseView

from .base import BreadTestCase
from .factories import BreadTestModelFactory


class BreadBrowseTest(BreadTestCase):
    @patch("bread.templatetags.bread_tags.logger")
    def test_get(self, mock_logger):
        self.set_urls(self.bread)
        items = [BreadTestModelFactory() for __ in range(5)]
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse"))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        self.assertTrue(rsp.context_data["bread_test_class"])
        body = rsp.content.decode("utf-8")
        for item in items:
            self.assertIn(item.name, body)
        # No exceptions logged
        self.assertFalse(mock_logger.exception.called)

    def test_get_empty_list(self):
        self.set_urls(self.bread)
        self.model.objects.all().delete()
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse"))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)

    def test_post(self):
        self.set_urls(self.bread)
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse"))
        request = self.request_factory.post(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(405, rsp.status_code)

    @patch("bread.templatetags.bread_tags.logger")
    def test_sort_all_ascending(self, mock_logger):
        self.set_urls(self.bread)
        BreadTestModelFactory(name="999", other__text="012", age=50)
        BreadTestModelFactory(name="555", other__text="333", age=60)
        BreadTestModelFactory(name="111", other__text="555", age=10)
        BreadTestModelFactory(name="111", other__text="555", age=20)
        BreadTestModelFactory(name="111", other__text="555", age=5)
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse")) + "?o=0,1"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        results = rsp.context_data["object_list"]
        i = 0
        while i < len(results) - 1:
            sortA = (results[i].name, results[i].other.text)
            sortB = (results[i + 1].name, results[i + 1].other.text)
            self.assertLessEqual(sortA, sortB)
            if sortA == sortB:
                # default sort is '-age'
                self.assertGreaterEqual(results[i].age, results[i + 1].age)
            i += 1
        # No exceptions logged
        self.assertFalse(mock_logger.exception.called)

    @patch("bread.templatetags.bread_tags.logger")
    def test_sort_most_ascending_with_override_default_order(self, mock_logger):
        self.set_urls(self.bread)
        self.bread.browse_view.default_ordering = ["-other__text", "age"]
        BreadTestModelFactory(name="999", other__text="012", age=50)
        BreadTestModelFactory(name="555", other__text="333", age=60)
        BreadTestModelFactory(name="111", other__text="555", age=10)
        BreadTestModelFactory(name="111", other__text="555", age=20)
        BreadTestModelFactory(name="111", other__text="555", age=5)
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse")) + "?o=0,1"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        results = rsp.context_data["object_list"]

        i = 0
        while i < len(results) - 1:
            sortA = (results[i].name, results[i].other.text)
            sortB = (results[i + 1].name, results[i + 1].other.text)
            self.assertLessEqual(sortA, sortB)
            if sortA == sortB:
                # default sort is 'age'
                self.assertLessEqual(results[i].age, results[i + 1].age)
            i += 1
        # No exceptions logged
        self.assertFalse(mock_logger.exception.called)

    @patch("bread.templatetags.bread_tags.logger")
    def test_sort_all_descending(self, mock_logger):
        self.set_urls(self.bread)
        BreadTestModelFactory(name="999", other__text="012", age=50)
        BreadTestModelFactory(name="555", other__text="333", age=60)
        BreadTestModelFactory(name="111", other__text="555", age=10)
        BreadTestModelFactory(name="111", other__text="555", age=20)
        BreadTestModelFactory(name="111", other__text="555", age=5)
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse")) + "?o=-0,-1"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        results = rsp.context_data["object_list"]
        i = 0
        while i < len(results) - 1:
            sortA = (results[i].name, results[i].other.text)
            sortB = (results[i + 1].name, results[i + 1].other.text)
            self.assertGreaterEqual(sortA, sortB)
            if sortA == sortB:
                # default sort is '-age'
                self.assertGreaterEqual(results[i].age, results[i + 1].age)
            i += 1
        # No exceptions logged
        self.assertFalse(mock_logger.exception.called)

    def test_sort_first_ascending(self):
        self.set_urls(self.bread)
        BreadTestModelFactory(name="999", other__text="012")
        BreadTestModelFactory(name="555", other__text="333")
        BreadTestModelFactory(name="111", other__text="555")
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse")) + "?o=0"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        results = rsp.context_data["object_list"]
        i = 0
        while i < len(results) - 1:
            sortA = (results[i].name, results[i].other.text)
            sortB = (results[i + 1].name, results[i + 1].other.text)
            self.assertLessEqual(sortA, sortB)
            i += 1

    def test_sort_first_ascending_second_descending(self):
        self.set_urls(self.bread)
        e = BreadTestModelFactory(name="999", other__text="012")
        d = BreadTestModelFactory(name="999", other__text="212")
        c = BreadTestModelFactory(name="999", other__text="312")
        a = BreadTestModelFactory(name="111", other__text="555")
        b = BreadTestModelFactory(name="555", other__text="333")
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse")) + "?o=0,-1"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        results = rsp.context_data["object_list"]
        self.assertEqual(a, results[0])
        self.assertEqual(b, results[1])
        self.assertEqual(c, results[2])
        self.assertEqual(d, results[3])
        self.assertEqual(e, results[4])

    def test_sort_first_descending_second_ascending(self):
        self.set_urls(self.bread)
        a = BreadTestModelFactory(name="999", other__text="012")
        b = BreadTestModelFactory(name="999", other__text="212")
        c = BreadTestModelFactory(name="999", other__text="312")
        e = BreadTestModelFactory(name="111", other__text="555")
        d = BreadTestModelFactory(name="555", other__text="333")
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse")) + "?o=-0,1"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        results = rsp.context_data["object_list"]
        self.assertEqual(a, results[0])
        self.assertEqual(b, results[1])
        self.assertEqual(c, results[2])
        self.assertEqual(d, results[3])
        self.assertEqual(e, results[4])

    def test_sort_second_field_ascending(self):
        self.set_urls(self.bread)
        d = BreadTestModelFactory(name="555", other__text="333")
        a = BreadTestModelFactory(name="999", other__text="012")
        c = BreadTestModelFactory(name="999", other__text="312")
        b = BreadTestModelFactory(name="999", other__text="212")
        e = BreadTestModelFactory(name="111", other__text="555")
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse")) + "?o=1"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        results = rsp.context_data["object_list"]
        self.assertEqual(a, results[0])
        self.assertEqual(b, results[1])
        self.assertEqual(c, results[2])
        self.assertEqual(d, results[3])
        self.assertEqual(e, results[4])

    @patch("bread.templatetags.bread_tags.logger")
    def test_sort_second_field_ascending_first_descending(self, mock_logger):
        self.set_urls(self.bread)
        d = BreadTestModelFactory(name="1", other__text="111")
        a = BreadTestModelFactory(name="999", other__text="000")
        e = BreadTestModelFactory(name="111", other__text="555")
        b = BreadTestModelFactory(name="3", other__text="111")
        c = BreadTestModelFactory(name="2", other__text="111")
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse")) + "?o=1,-0"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        results = rsp.context_data["object_list"]
        self.assertEqual(a, results[0])
        self.assertEqual(b, results[1])
        self.assertEqual(c, results[2])
        self.assertEqual(d, results[3])
        self.assertEqual(e, results[4])
        # No exceptions logged
        self.assertFalse(mock_logger.exception.called)


class BadSortTest(BreadTestCase):
    class BrowseClass(BrowseView):
        columns = [("Name", "name"), ("Text", "other__get_text")]

    extra_bread_attributes = {
        "browse_view": BrowseClass,
    }

    def test_unorderable_column(self):
        self.set_urls(self.bread)
        BreadTestModelFactory(name="1", other__text="111")
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse")) + "?o=1,-0"
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(400, rsp.status_code)


class NotDisablingSortTest(BreadTestCase):
    class BrowseClass(BrowseView):
        columns = [
            ("Name", "name"),
        ]

    extra_bread_attributes = {
        "browse_view": BrowseClass,
    }

    def test_sorting_on_column(self):
        # 'name' is a valid column to sort on
        # (we test this because otherwise the DisableSortTest test isn't valid)
        self.set_urls(self.bread)
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse"))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        self.assertEqual(
            [0], json.loads(rsp.context_data["valid_sorting_columns_json"])
        )


class DisableSortTest(BreadTestCase):
    class BrowseClass(BrowseView):
        columns = [
            ("Name", "name", False),
        ]

    extra_bread_attributes = {
        "browse_view": BrowseClass,
    }

    def test_not_sorting_on_column(self):
        self.set_urls(self.bread)
        self.give_permission("browse")
        url = reverse(self.bread.get_url_name("browse"))
        request = self.request_factory.get(url)
        request.user = self.user
        rsp = self.bread.get_browse_view()(request)
        self.assertEqual(200, rsp.status_code)
        rsp.render()
        self.assertEqual([], json.loads(rsp.context_data["valid_sorting_columns_json"]))
