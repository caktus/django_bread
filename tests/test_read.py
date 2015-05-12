from six.moves.http_client import OK, METHOD_NOT_ALLOWED

from django.core.urlresolvers import reverse
from django.http import Http404

from .base import BreadTestCase
from .models import BreadLabelValueTestModel
from .factories import BreadLabelValueTestModelFactory
from bread.bread import LabelValueReadView, Bread


class BreadReadTest(BreadTestCase):
    def setUp(self):
        super(BreadReadTest, self).setUp()
        self.urlconf = 'bread.tests.test_read'
        self.give_permission('read')
        self.set_urls(self.bread)

    def test_read(self):
        item = self.model_factory()
        url = reverse('read_%s' % self.model_name, kwargs={'pk': item.pk})
        request = self.request_factory.get(url)
        request.user = self.user

        view = self.bread.get_read_view()
        rsp = view(request, pk=item.pk)

        self.assertEqual(OK, rsp.status_code)
        rsp.render()
        body = rsp.content.decode('utf-8')
        self.assertIn(item.name, body)

    def test_read_no_such_item(self):
        self.assertFalse(self.model.objects.filter(pk=999).exists())
        url = reverse('read_%s' % self.model_name, kwargs={'pk': 999})
        request = self.request_factory.get(url)
        request.user = self.user

        view = self.bread.get_read_view()
        with self.assertRaises(Http404):
            view(request, pk=999)

    def test_post(self):
        self.set_urls(self.bread)
        self.give_permission('read')
        item = self.model_factory()
        url = reverse(self.bread.get_url_name('read'), kwargs={'pk': item.pk})
        request = self.request_factory.post(url)
        request.user = self.user
        rsp = self.bread.get_read_view()(request)
        self.assertEqual(METHOD_NOT_ALLOWED, rsp.status_code)


class BreadLabelValueReadTest(BreadTestCase):
    """Exercise LabelValueReadView, particularly the 5 modes described in get_field_label_value()"""
    def setUp(self):
        super(BreadLabelValueReadTest, self).setUp()

        class ReadClass(LabelValueReadView):
            """See LabelValueReadView.get_field_label_value() for descriptions of the modes"""
            fields = [
                (None, 'id'),                        # Mode 1, also test of None for label.
                (None, 'banana'),                    # Same, also test field w/explicit verbose_name
                ('eman', 'name_reversed'),           # Mode 2
                ('Foo', 'bar'),                      # Mode 3
                ('context first key', lambda context_data: list(context_data.keys())[0]),  # Mode 4
                ('Answer', 42),                      # Mode 5
            ]

        class BreadTestClass(Bread):
            model = BreadLabelValueTestModel
            base_template = 'bread/empty.html'
            read_view = ReadClass

        self.bread = BreadTestClass()

        self.model = BreadLabelValueTestModel
        self.model_name = self.model._meta.model_name
        self.model_factory = BreadLabelValueTestModelFactory

        self.urlconf = 'bread.tests.test_read'
        self.give_permission('read')
        self.set_urls(self.bread)

    def test_read(self):
        item = BreadLabelValueTestModel(name='abcde')
        item.save()
        url = reverse('read_%s' % self.model_name, kwargs={'pk': item.pk})
        request = self.request_factory.get(url)
        request.user = self.user

        view = self.bread.get_read_view()
        rsp = view(request, pk=item.pk)

        self.assertEqual(OK, rsp.status_code)
        rsp.render()
        body = rsp.content.decode('utf-8')
        self.assertIn('bar', body)

        # Test get_field_label_value() by checking the rendering of the the 5 fields of
        # TestLabelValueBreadReadView.
        key = list(rsp.context_data.keys())[0]
        for expected in (
            "<label>Id</label>: <span class='value'>{}</span>".format(item.id),
            "<label>A Yellow Fruit</label>: <span class='value'>0</span>",
            "<label>Eman</label>: <span class='value'>edcba</span>",
            "<label>Foo</label>: <span class='value'>bar</span>",
            "<label>Context first key</label>: <span class='value'>{}</span>".format(key),
            "<label>Answer</label>: <span class='value'>42</span>",
                ):
            self.assertContains(rsp, expected)
