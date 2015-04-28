from django.test import override_settings
from .base import BreadTestCase


class BreadDefaultTemplateResolutionTest(BreadTestCase):

    def test_template_resolution(self):
        # skip 'add' since it uses 'edit' template
        bread_names = ['browse', 'read', 'edit', 'delete']
        app_name = self.model._meta.app_label
        for bread_name in bread_names:
            vanilla_template_name = '%s/%s%s.html' % (app_name, self.model_name, bread_name)
            default_bread_template_name = 'bread/%s.html' % (bread_name, )
            expected_templates = [
                vanilla_template_name,
                default_bread_template_name,
            ]
            get_method_name = 'base_%s_view_class' % (bread_name, )
            view_class = getattr(self.bread, get_method_name)
            view = view_class(bread=self.bread, model=self.bread.model)
            self.assertEqual(view.get_template_names(), expected_templates)


@override_settings(BREAD={'DEFAULT_TEMPLATE_NAME_PATTERN': 'mysite/bread/{view}.html'})
class BreadCustomizedTemplateResolutionTest(BreadTestCase):

    def test_template_resolution(self):
        # skip 'add' since it uses 'edit' template
        bread_names = ['browse', 'read', 'edit', 'delete']
        app_name = self.model._meta.app_label
        for bread_name in bread_names:
            vanilla_template_name = '%s/%s%s.html' % (app_name, self.model_name, bread_name)
            custom_template_name = 'mysite/bread/%s.html' % (bread_name, )
            default_bread_template_name = 'bread/%s.html' % (bread_name, )
            expected_templates = [
                vanilla_template_name,
                custom_template_name,
                default_bread_template_name,
            ]
            get_method_name = 'base_%s_view_class' % (bread_name, )
            view_class = getattr(self.bread, get_method_name)
            view = view_class(bread=self.bread, model=self.bread.model)
            self.assertEqual(view.get_template_names(), expected_templates)
