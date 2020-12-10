from .base import BreadTestCase


class BreadURLsNamespaceTest(BreadTestCase):
    url_namespace = "testns"

    def test_all_views_urls_with_namespace(self):
        # get_urls() returns the expected URL patterns
        bread = self.bread
        patterns = bread.get_urls()

        self.assertEqual(
            set(
                [
                    bread.browse_url_name(include_namespace=False),
                    bread.read_url_name(include_namespace=False),
                    bread.edit_url_name(include_namespace=False),
                    bread.add_url_name(include_namespace=False),
                    bread.delete_url_name(include_namespace=False),
                ]
            ),
            set([x.name for x in patterns]),
        )

        self.assertTrue(bread.browse_url_name().startswith(self.url_namespace + ":"))
        self.assertTrue(bread.read_url_name().startswith(self.url_namespace + ":"))
        self.assertTrue(bread.edit_url_name().startswith(self.url_namespace + ":"))
        self.assertTrue(bread.add_url_name().startswith(self.url_namespace + ":"))
        self.assertTrue(bread.delete_url_name().startswith(self.url_namespace + ":"))
        self.assertFalse(
            bread.browse_url_name(include_namespace=False).startswith(
                self.url_namespace + ":"
            )
        )
        self.assertFalse(
            bread.read_url_name(include_namespace=False).startswith(
                self.url_namespace + ":"
            )
        )
        self.assertFalse(
            bread.edit_url_name(include_namespace=False).startswith(
                self.url_namespace + ":"
            )
        )
        self.assertFalse(
            bread.add_url_name(include_namespace=False).startswith(
                self.url_namespace + ":"
            )
        )
        self.assertFalse(
            bread.delete_url_name(include_namespace=False).startswith(
                self.url_namespace + ":"
            )
        )

        browse_pattern = [
            x
            for x in patterns
            if x.name == bread.browse_url_name(include_namespace=False)
        ][0].pattern
        self.assertEqual("%s/" % self.bread.plural_name, str(browse_pattern))

        read_pattern = [
            x
            for x in patterns
            if x.name == bread.read_url_name(include_namespace=False)
        ][0].pattern
        self.assertEqual("%s/<int:pk>/" % self.bread.plural_name, str(read_pattern))

        edit_pattern = [
            x
            for x in patterns
            if x.name == bread.edit_url_name(include_namespace=False)
        ][0].pattern
        self.assertEqual(
            "%s/<int:pk>/edit/" % self.bread.plural_name, str(edit_pattern)
        )


class BreadURLsTest(BreadTestCase):
    def test_all_views_urls_no_namespace(self):
        # get_urls() returns the expected URL patterns
        bread = self.bread
        patterns = bread.get_urls()

        self.assertEqual(
            set(
                [
                    bread.browse_url_name(),
                    bread.read_url_name(),
                    bread.edit_url_name(),
                    bread.add_url_name(),
                    bread.delete_url_name(),
                ]
            ),
            set([x.name for x in patterns]),
        )

        browse_pattern = [x for x in patterns if x.name == bread.browse_url_name()][
            0
        ].pattern
        self.assertEqual("%s/" % bread.plural_name, str(browse_pattern))

        read_pattern = [x for x in patterns if x.name == bread.read_url_name()][
            0
        ].pattern
        self.assertEqual("%s/<int:pk>/" % bread.plural_name, str(read_pattern))

        edit_pattern = [x for x in patterns if x.name == bread.edit_url_name()][
            0
        ].pattern
        self.assertEqual("%s/<int:pk>/edit/" % bread.plural_name, str(edit_pattern))

    def test_view_subset(self):
        # We can do bread with a subset of the BREAD views
        self.bread.views = "B"
        url_names = [x.name for x in self.bread.get_urls()]
        self.assertIn("browse_%s" % self.bread.plural_name, url_names)
        self.assertNotIn("read_%s" % self.model_name, url_names)
        self.assertNotIn("edit_%s" % self.model_name, url_names)
        self.assertNotIn("add_%s" % self.model_name, url_names)
        self.assertNotIn("delete_%s" % self.model_name, url_names)

        self.bread.views = "RE"
        url_names = [x.name for x in self.bread.get_urls()]
        self.assertNotIn("browse_%s" % self.bread.plural_name, url_names)
        self.assertIn("read_%s" % self.model_name, url_names)
        self.assertIn("edit_%s" % self.model_name, url_names)
        self.assertNotIn("add_%s" % self.model_name, url_names)
        self.assertNotIn("delete_%s" % self.model_name, url_names)

    def test_url_names(self):
        # The xxxx_url_name methods return what we expect
        bread = self.bread
        self.assertEqual("browse_%s" % self.bread.plural_name, bread.browse_url_name())
        self.assertEqual("read_%s" % self.model_name, bread.read_url_name())
        self.assertEqual("edit_%s" % self.model_name, bread.edit_url_name())
        self.assertEqual("add_%s" % self.model_name, bread.add_url_name())
        self.assertEqual("delete_%s" % self.model_name, bread.delete_url_name())

    def test_omit_prefix(self):
        bread = self.bread
        patterns = bread.get_urls(prefix=False)

        self.assertEqual(
            set(
                [
                    bread.browse_url_name(),
                    bread.read_url_name(),
                    bread.edit_url_name(),
                    bread.add_url_name(),
                    bread.delete_url_name(),
                ]
            ),
            set([x.name for x in patterns]),
        )

        browse_pattern = [x for x in patterns if x.name == bread.browse_url_name()][
            0
        ].pattern
        self.assertEqual("", str(browse_pattern))

        read_pattern = [x for x in patterns if x.name == bread.read_url_name()][
            0
        ].pattern
        self.assertEqual("<int:pk>/", str(read_pattern))

        edit_pattern = [x for x in patterns if x.name == bread.edit_url_name()][
            0
        ].pattern
        self.assertEqual("<int:pk>/edit/", str(edit_pattern))
