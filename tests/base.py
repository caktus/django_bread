from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase, override_settings

from bread.bread import Bread, BrowseView, ReadView

from .factories import BreadTestModelFactory
from .models import BreadTestModel

# Set urlpatterns for a test by calling .set_urls()
urlpatterns = None


@override_settings(
    ROOT_URLCONF="tests.base",
    BREAD={
        "DEFAULT_BASE_TEMPLATE": "bread/empty.html",
    },
)
class BreadTestCase(TestCase):
    url_namespace = ""
    extra_bread_attributes = {}

    def setUp(self):
        self.username = "joe"
        self.password = "random"
        User = get_user_model()
        self.user = User.objects.create_user(username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        assert self.client.login(username=self.username, password=self.password)
        self.model = BreadTestModel
        self.model_name = self.model._meta.model_name
        self.model_factory = BreadTestModelFactory
        self.request_factory = RequestFactory()

        class ReadClass(ReadView):
            columns = [
                ("Name", "name"),
                ("Text", "other__text"),
                (
                    "Model1",
                    "model1",
                ),
            ]

        class BrowseClass(BrowseView):
            columns = [
                ("Name", "name"),
                ("Text", "other__text"),
                ("Model1", "model1"),
                ("Roundabout Name", "get_name"),
            ]

        class BreadTestClass(Bread):
            model = self.model
            base_template = "bread/empty.html"
            browse_view = BrowseClass
            namespace = self.url_namespace
            plural_name = "testmodels"

            def get_additional_context_data(self):
                context = super(BreadTestClass, self).get_additional_context_data()
                context["bread_test_class"] = True
                return context

        for k, v in self.extra_bread_attributes.items():
            setattr(BreadTestClass, k, v)

        self.BreadTestClass = BreadTestClass
        self.bread = BreadTestClass()

    def tearDown(self):
        global urlpatterns
        urlpatterns = None

    def set_urls(self, bread):
        # Given a bread instance, set its URLs on the test urlconf
        global urlpatterns
        urlpatterns = bread.get_urls()

    def get_permission(self, short_name):
        """Return a Permission object for the test model.
        short_name should be browse, read, edit, add, or delete.
        """
        return Permission.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self.model),
            codename="%s_%s" % (short_name, self.model_name),
        )[0]

    def give_permission(self, short_name):
        self.user.user_permissions.add(self.get_permission(short_name))
