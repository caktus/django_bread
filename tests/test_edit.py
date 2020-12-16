from django import forms
from django.urls import reverse

from bread.bread import Bread, EditView

from .base import BreadTestCase
from .models import BreadTestModel


class BreadEditTest(BreadTestCase):
    def setUp(self):
        super(BreadEditTest, self).setUp()
        self.set_urls(self.bread)

    def test_edit_item(self):
        item = self.model_factory()
        url = reverse(self.bread.get_url_name("edit"), kwargs={"pk": item.pk})
        request = self.request_factory.post(
            url, data={"name": "Fred Jones", "age": "19"}
        )
        request.user = self.user
        self.give_permission("change")
        view = self.bread.get_edit_view()
        rsp = view(request, pk=item.pk)
        self.assertEqual(302, rsp.status_code)
        self.assertEqual(reverse(self.bread.get_url_name("browse")), rsp["Location"])
        item = self.model.objects.get(pk=item.pk)
        self.assertEqual("Fred Jones", item.name)

    def test_fail_validation(self):
        item = self.model_factory()
        url = reverse(self.bread.get_url_name("edit"), kwargs={"pk": item.pk})
        request = self.request_factory.post(
            url, data={"name": "this name is too much long yeah", "age": "19"}
        )
        request.user = self.user
        self.give_permission("change")
        view = self.bread.get_edit_view()
        rsp = view(request, pk=item.pk)
        self.assertEqual(400, rsp.status_code)
        self.assertTrue(rsp.context_data["bread_test_class"])
        context = rsp.context_data
        form = context["form"]
        errors = form.errors
        self.assertIn("name", errors)

    def test_get(self):
        # Get should give you a form with the item filled in
        item = self.model_factory()
        url = reverse(self.bread.get_url_name("edit"), kwargs={"pk": item.pk})
        request = self.request_factory.get(url)
        request.user = self.user
        self.give_permission("change")
        view = self.bread.get_edit_view()
        rsp = view(request, pk=item.pk)
        self.assertEqual(200, rsp.status_code)
        form = rsp.context_data["form"]
        self.assertFalse(form.is_bound)
        self.assertEqual(item.pk, form.initial["id"])
        self.assertEqual(item.name, form.initial["name"])
        rsp.render()
        body = rsp.content.decode("utf-8")
        self.assertIn('method="POST"', body)

    def test_setting_form_class(self):
        class DummyForm(forms.Form):
            pass

        glob = {}

        class TestView(EditView):
            form_class = DummyForm

            # To get hold of a reference to the actual view object created by
            # bread, use a fake dispatch method that saves 'self' into a
            # dictionary we can access in the test.
            def dispatch(self, *args, **kwargs):
                glob["view_object"] = self

        class BreadTest(Bread):
            model = BreadTestModel
            edit_view = TestView

        bread = BreadTest()
        view_function = bread.get_edit_view()
        # Call the view function to invoke dispatch so we can get to the view itself
        view_function(None, None, None)
        self.assertEqual(DummyForm, glob["view_object"].form_class)
