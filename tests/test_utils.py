from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.test import TestCase

from bread.utils import (
    get_model_field,
    get_verbose_name,
    has_required_args,
    validate_fieldspec,
)
from tests.models import BreadLabelValueTestModel, BreadTestModel, BreadTestModel2


class HasRequiredArgsTestCase(TestCase):
    def test_simple_no_args_function(self):
        def testfunc():
            pass

        self.assertFalse(has_required_args(testfunc))

    def test_simple_1_arg_function(self):
        def testfunc(foo):
            pass

        self.assertTrue(has_required_args(testfunc))

    def test_simple_1_arg_function_with_default(self):
        def testfunc(foo=2):
            pass

        self.assertFalse(has_required_args(testfunc))

    def test_simple_2_arg_function(self):
        def testfunc(foo, bar):
            pass

        self.assertTrue(has_required_args(testfunc))

    def test_simple_2_arg_function_with_one_default(self):
        def testfunc(foo, bar=3):
            pass

        self.assertTrue(has_required_args(testfunc))

    def test_simple_2_arg_function_with_two_defaults(self):
        def testfunc(foo=1, bar=3):
            pass

        self.assertFalse(has_required_args(testfunc))

    def test_class_function_no_args(self):
        class TestClass(object):
            def func(self):
                pass

        self.assertFalse(has_required_args(TestClass.func))

    def test_class_function_1_arg(self):
        class TestClass(object):
            def func(self, foo):
                pass

        self.assertTrue(has_required_args(TestClass.func))

    def test_class_function_1_arg_with_default(self):
        class TestClass(object):
            def func(self, foo=2):
                pass

        self.assertFalse(has_required_args(TestClass.func))

    def test_class_function_2_args(self):
        class TestClass(object):
            def func(self, foo, bar):
                pass

        self.assertTrue(has_required_args(TestClass.func))

    def test_class_function_2_args_1_default(self):
        class TestClass(object):
            def func(self, foo, bar=2):
                pass

        self.assertTrue(has_required_args(TestClass.func))

    def test_class_function_2_args_2_defaults(self):
        class TestClass(object):
            def func(self, foo=1, bar=2):
                pass

        self.assertFalse(has_required_args(TestClass.func))


class GetModelFieldTestCase(TestCase):
    def test_it(self):
        obj3 = BreadLabelValueTestModel.objects.create(name="Species")
        obj2 = BreadTestModel2.objects.create(text="Rhinocerous", label_model=obj3)
        obj1 = BreadTestModel.objects.create(name="Rudy Vallee", other=obj2, age=72)
        self.assertEqual(obj1.name, get_model_field(obj1, "name"))
        self.assertEqual(obj1.name, get_model_field(obj1, "get_name"))

        self.assertEqual(obj2.text, get_model_field(obj1, "other__text"))
        self.assertEqual(obj2.text, get_model_field(obj1, "other__get_text"))

        # Prove that we can call a dunder method.
        self.assertEqual(obj1.name, get_model_field(obj1, "__str__"))

        # Prove that we can traverse reverse OneToOneRel fields
        self.assertEqual(obj2.text, get_model_field(obj3, "model2__text"))


class ValidateFieldspecTestCase(TestCase):
    def test_simple_field(self):
        validate_fieldspec(BreadTestModel, "name")

    def test_method_name(self):
        validate_fieldspec(BreadTestModel, "get_name")

    def test_method_with_optional_arg(self):
        validate_fieldspec(BreadTestModel, "method2")

    def test_method_with_required_arg(self):
        with self.assertRaises(ValidationError):
            validate_fieldspec(BreadTestModel, "method1")

    def test_no_such_attribute(self):
        with self.assertRaises(ValidationError):
            validate_fieldspec(BreadTestModel, "petunias")

    def test_get_other(self):
        validate_fieldspec(BreadTestModel, "other")

    def test_field_on_other(self):
        validate_fieldspec(BreadTestModel, "other__text")

    def test_method_on_other(self):
        validate_fieldspec(BreadTestModel, "other__get_text")

    def test_no_such_attribute_on_other(self):
        with self.assertRaises(ValidationError):
            validate_fieldspec(BreadTestModel, "other__petunias")

    def test_reverse_one_to_one_rel(self):
        validate_fieldspec(BreadLabelValueTestModel, "model2__text")


class GetVerboseNameTest(TestCase):
    """Exercise get_verbose_name()"""

    def test_with_model(self):
        """Ensure a model is accepted as a param"""
        self.assertEqual(
            get_verbose_name(BreadLabelValueTestModel, "banana"), "A Yellow Fruit"
        )

    def test_with_instance(self):
        """Ensure a model instance is accepted as a param"""
        self.assertEqual(
            get_verbose_name(BreadLabelValueTestModel(), "banana"), "A Yellow Fruit"
        )

    def test_no_title_cap(self):
        """Ensure title cap is optional"""
        self.assertEqual(
            get_verbose_name(BreadLabelValueTestModel, "banana", False),
            "a yellow fruit",
        )

    def test_field_with_no_explicit_verbose_name(self):
        """Test behavior with a field to which we haven't given an explicit name"""
        self.assertEqual(get_verbose_name(BreadLabelValueTestModel, "id"), "Id")

    def test_failure(self):
        """Ensure FieldDoesNotExist is raised no matter what trash is passed as the field name"""
        for field_name in (
            "kjasfhkjdh",
            u"sfasfda",
            None,
            42,
            False,
            complex(42),
            lambda: None,
            ValueError(),
            {},
            [],
            tuple(),
        ):
            with self.assertRaises(FieldDoesNotExist):
                get_verbose_name(BreadLabelValueTestModel, field_name)
