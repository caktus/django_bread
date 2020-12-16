from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse

from .base import BreadTestCase
from .models import BreadTestModel


class TestForm(forms.ModelForm):
    # A form we override the bread form with
    # It only allows names that start with 'Dan'
    class Meta:
        model = BreadTestModel
        fields = ["name", "age"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        if not name.startswith("Dan"):
            raise ValidationError("All good names start with Dan")
        return name


class BreadFormAddTest(BreadTestCase):
    extra_bread_attributes = {
        "form_class": TestForm,
    }

    def setUp(self):
        super(BreadFormAddTest, self).setUp()
        self.set_urls(self.bread)

    def test_new_item(self):
        self.model.objects.all().delete()
        url = reverse(self.bread.get_url_name("add"))
        request = self.request_factory.post(
            url, data={"name": "Dan Jones", "age": "19"}
        )
        request.user = self.user
        self.give_permission("add")
        view = self.bread.get_add_view()
        rsp = view(request)
        self.assertEqual(302, rsp.status_code)
        self.assertEqual(reverse(self.bread.get_url_name("browse")), rsp["Location"])
        item = self.model.objects.get()
        self.assertEqual("Dan Jones", item.name)

    def test_fail_validation(self):
        self.model.objects.all().delete()
        url = reverse(self.bread.get_url_name("add"))
        request = self.request_factory.post(url, data={"name": "Fred", "age": "19"})
        request.user = self.user
        self.give_permission("add")
        view = self.bread.get_add_view()
        rsp = view(request)
        self.assertEqual(400, rsp.status_code)
        context = rsp.context_data
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


class BreadFormEditTest(BreadTestCase):
    extra_bread_attributes = {
        "form_class": TestForm,
    }

    def setUp(self):
        super(BreadFormEditTest, self).setUp()
        self.set_urls(self.bread)

    def test_edit_item(self):
        item = self.model_factory()
        url = reverse(self.bread.get_url_name("edit"), kwargs={"pk": item.pk})
        request = self.request_factory.post(
            url, data={"name": "Dan Jones", "age": "19"}
        )
        request.user = self.user
        self.give_permission("change")
        view = self.bread.get_edit_view()
        rsp = view(request, pk=item.pk)
        self.assertEqual(302, rsp.status_code)
        self.assertEqual(reverse(self.bread.get_url_name("browse")), rsp["Location"])
        item = self.model.objects.get(pk=item.pk)
        self.assertEqual("Dan Jones", item.name)

    def test_fail_validation(self):
        item = self.model_factory()
        url = reverse(self.bread.get_url_name("edit"), kwargs={"pk": item.pk})
        request = self.request_factory.post(url, data={"name": "Fred", "age": "19"})
        request.user = self.user
        self.give_permission("change")
        view = self.bread.get_edit_view()
        rsp = view(request, pk=item.pk)
        self.assertEqual(400, rsp.status_code)
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
        self.assertEqual(item.name, form.initial["name"])
        rsp.render()
        body = rsp.content.decode("utf-8")
        self.assertIn('method="POST"', body)


class BreadExcludeTest(BreadTestCase):
    # We can exclude a field from the default form
    extra_bread_attributes = {"exclude": ["id"]}

    def setUp(self):
        super(BreadExcludeTest, self).setUp()
        self.set_urls(self.bread)

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
        self.assertNotIn("id", form.initial)
        self.assertEqual(item.name, form.initial["name"])
