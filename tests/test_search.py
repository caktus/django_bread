# coding: utf-8
from bread.bread import Bread, BrowseView
from tests.base import BreadTestCase
from tests.factories import BreadTestModelFactory
from tests.models import BreadTestModel


class BrowseSearchView(BrowseView):
    search_fields = ["name", "other__text"]


class BreadSearchView(Bread):
    # Bread view with search fields defined
    base_template = "bread/empty.html"
    browse_view = BrowseSearchView
    model = BreadTestModel
    views = "B"


class BreadNoSearchView(Bread):
    # Default bread view - no search fields defined
    base_template = "bread/empty.html"
    model = BreadTestModel
    views = "B"


class BreadSearchTestCase(BreadTestCase):
    def setUp(self):
        super(BreadSearchTestCase, self).setUp()
        self.bread = BreadSearchView()
        self.view = self.bread.get_browse_view()
        self.give_permission("browse")

        self.joe = BreadTestModelFactory(name="Joe", other__text="Smith")
        self.jim = BreadTestModelFactory(name="Jim", other__text="Brown")

    def get_search_results(self, q=None):
        data = {}
        if q is not None:
            data["q"] = q
        request = self.request_factory.get("", data=data)
        request.user = self.user
        rsp = self.view(request)
        self.assertEqual(200, rsp.status_code)
        return rsp.context_data["object_list"]

    def test_no_query_parm(self):
        objs = self.get_search_results()
        self.assertEqual(BreadTestModel.objects.count(), len(objs))

    def test_simple_search_direct_field(self):
        objs = self.get_search_results(q="Joe")
        obj_ids = [obj.id for obj in objs]
        self.assertEqual([self.joe.id], obj_ids)

    def test_simple_search_any_field(self):
        # All records that match any field are returned
        objs = self.get_search_results(q="i")
        self.assertEqual(2, len(objs))

    def test_simple_search_indirect_field(self):
        objs = self.get_search_results(q="Smith")
        obj_ids = [obj.id for obj in objs]
        self.assertEqual([self.joe.id], obj_ids)

    def test_multiple_terms_match(self):
        # A record that matches all terms is returned
        objs = self.get_search_results(q="Joe Smith")
        obj_ids = [obj.id for obj in objs]
        self.assertEqual([self.joe.id], obj_ids)

    def test_multiple_terms_dont_match(self):
        # All terms must match the record
        objs = self.get_search_results(q="Joe Brown")
        self.assertEqual(0, len(objs))

    def test_case_insensitive(self):
        objs = self.get_search_results(q="joe")
        obj_ids = [obj.id for obj in objs]
        self.assertEqual([self.joe.id], obj_ids)

    def test_nonascii_search(self):
        # This was failing if we were also paginating
        BreadTestModelFactory(name=u"قمر")
        BreadTestModelFactory(name=u"قمر")
        try:
            self.bread.browse_view.paginate_by = 1
            self.get_search_results(q=u"قمر")
        finally:
            self.bread.browse_view.paginate_by = None
