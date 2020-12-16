from django import forms
from django.http import Http404
from django.urls import reverse

from bread.bread import Bread, LabelValueReadView, ReadView

from .base import BreadTestCase
from .factories import BreadLabelValueTestModelFactory
from .models import BreadLabelValueTestModel, BreadTestModel


class BreadReadTest(BreadTestCase):
    def setUp(self):
        super(BreadReadTest, self).setUp()
        self.urlconf = "bread.tests.test_read"
        self.give_permission("view")
        self.set_urls(self.bread)

    def test_read(self):
        item = self.model_factory()
        url = reverse("read_%s" % self.model_name, kwargs={"pk": item.pk})
        request = self.request_factory.get(url)
        request.user = self.user

        view = self.bread.get_read_view()
        rsp = view(request, pk=item.pk)

        self.assertEqual(200, rsp.status_code)
        rsp.render()
        self.assertTrue(rsp.context_data["bread_test_class"])
        body = rsp.content.decode("utf-8")
        self.assertIn(item.name, body)

    def test_read_no_such_item(self):
        self.assertFalse(self.model.objects.filter(pk=999).exists())
        url = reverse("read_%s" % self.model_name, kwargs={"pk": 999})
        request = self.request_factory.get(url)
        request.user = self.user

        view = self.bread.get_read_view()
        with self.assertRaises(Http404):
            view(request, pk=999)

    def test_post(self):
        self.set_urls(self.bread)
        self.give_permission("view")
        item = self.model_factory()
        url = reverse(self.bread.get_url_name("read"), kwargs={"pk": item.pk})
        request = self.request_factory.post(url)
        request.user = self.user
        rsp = self.bread.get_read_view()(request)
        self.assertEqual(405, rsp.status_code)


class BreadLabelValueReadTest(BreadTestCase):
    """Exercise LabelValueReadView, particularly the 5 modes described in get_field_label_value()"""

    def setUp(self):
        super(BreadLabelValueReadTest, self).setUp()

        class ReadClass(LabelValueReadView):
            """See LabelValueReadView.get_field_label_value() for descriptions of the modes"""

            fields = [
                (None, "id"),  # Mode 1, also test of None for label.
                (None, "banana"),  # Same, also test field w/explicit verbose_name
                ("eman", "name_reversed"),  # Mode 2
                ("Foo", "bar"),  # Mode 3
                # Mode 4 below
                (
                    "context first key",
                    lambda context_data: sorted(context_data.keys())[0],
                ),
                ("Answer", 42),  # Mode 5
                ("Model2", "model2"),  # Back through related name for one2one field
            ]

        class BreadTestClass(Bread):
            model = BreadLabelValueTestModel
            base_template = "bread/empty.html"
            read_view = ReadClass

        self.bread = BreadTestClass()

        self.model = BreadLabelValueTestModel
        self.model_name = self.model._meta.model_name
        self.model_factory = BreadLabelValueTestModelFactory

        self.urlconf = "bread.tests.test_read"
        self.give_permission("view")
        self.set_urls(self.bread)

    def test_read(self):
        item = BreadLabelValueTestModel(name="abcde")
        item.save()
        url = reverse("read_%s" % self.model_name, kwargs={"pk": item.pk})
        request = self.request_factory.get(url)
        request.user = self.user

        view = self.bread.get_read_view()
        rsp = view(request, pk=item.pk)

        self.assertEqual(200, rsp.status_code)
        rsp.render()
        body = rsp.content.decode("utf-8")
        self.assertIn("bar", body)

        # Test get_field_label_value() by checking the rendering of the the 5 fields of
        # TestLabelValueBreadReadView.
        key = sorted(rsp.context_data.keys())[0]
        for expected in (
            "<label>Id</label>: <span class='value'>{}</span>".format(item.id),
            "<label>A Yellow Fruit</label>: <span class='value'>0</span>",
            "<label>eman</label>: <span class='value'>edcba</span>",
            "<label>Foo</label>: <span class='value'>bar</span>",
            "<label>context first key</label>: <span class='value'>{}</span>".format(
                key
            ),
            "<label>Answer</label>: <span class='value'>42</span>",
        ):
            self.assertContains(rsp, expected)

    def test_setting_form_class(self):
        class DummyForm(forms.Form):
            pass

        glob = {}

        class TestView(ReadView):
            form_class = DummyForm

            # To get hold of a reference to the actual view object created by
            # bread, use a fake dispatch method that saves 'self' into a
            # dictionary we can access in the test.
            def dispatch(self, *args, **kwargs):
                glob["view_object"] = self

        class BreadTest(Bread):
            model = BreadTestModel
            read_view = TestView

        bread = BreadTest()
        view_function = bread.get_read_view()
        # Call the view function to invoke dispatch so we can get to the view itself
        view_function(None, None, None)
        self.assertEqual(DummyForm, glob["view_object"].form_class)
