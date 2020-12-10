from django import forms
from django.urls import reverse

from bread.bread import AddView, Bread

from .base import BreadTestCase
from .models import BreadTestModel


class BreadAddTest(BreadTestCase):
    def setUp(self):
        super(BreadAddTest, self).setUp()
        self.set_urls(self.bread)

    def test_new_item(self):
        self.model.objects.all().delete()
        url = reverse(self.bread.get_url_name("add"))
        request = self.request_factory.post(
            url, data={"name": "Fred Jones", "age": "19"}
        )
        request.user = self.user
        self.give_permission("add")
        view = self.bread.get_add_view()
        rsp = view(request)
        self.assertEqual(302, rsp.status_code)
        self.assertEqual(reverse(self.bread.get_url_name("browse")), rsp["Location"])
        item = self.model.objects.get()
        self.assertEqual("Fred Jones", item.name)

    def test_fail_validation(self):
        self.model.objects.all().delete()
        url = reverse(self.bread.get_url_name("add"))
        request = self.request_factory.post(
            url, data={"name": "this name is too much long yeah", "age": "19"}
        )
        request.user = self.user
        self.give_permission("add")
        view = self.bread.get_add_view()
        rsp = view(request)
        self.assertEqual(400, rsp.status_code)
        context = rsp.context_data
        self.assertTrue(context["bread_test_class"])
        form = context["form"]
        errors = form.errors
        self.assertIn("name", errors)

    def test_get(self):
        # Get should give you a blank form
        url = reverse(self.bread.get_url_name("add"))
        request = self.request_factory.get(url)
        request.user = self.user
        self.give_permission("add")
        view = self.bread.get_add_view()
        rsp = view(request)
        self.assertEqual(200, rsp.status_code)
        form = rsp.context_data["form"]
        self.assertFalse(form.is_bound)
        rsp.render()
        body = rsp.content.decode("utf-8")
        self.assertIn('method="POST"', body)

    def test_setting_form_class(self):
        class DummyForm(forms.Form):
            pass

        glob = {}

        class TestAddView(AddView):
            form_class = DummyForm

            # To get hold of a reference to the actual view object created by
            # bread, use a fake dispatch method that saves 'self' into a
            # dictionary we can access in the test.
            def dispatch(self, *args, **kwargs):
                glob["view_object"] = self

        class BreadTest(Bread):
            model = BreadTestModel
            add_view = TestAddView

        bread = BreadTest()
        view_function = bread.get_add_view()
        # Call the  view function to invoke dispatch so we can get to the view itself
        view_function(None, None, None)
        self.assertEqual(DummyForm, glob["view_object"].form_class)
